use crate::flow::{ClosedFlow, ScheduledFlow};
use crate::metrics::RuntimeMetrics;
use serde::Serialize;
use std::sync::atomic::Ordering;
use std::time::Instant;

#[derive(Clone, Debug, Serialize)]
pub struct AdaptiveBudgetSnapshot {
    pub schema_version: u32,
    pub strategy: &'static str,
    pub configured_budget_us: f64,
    pub safety_ratio: f64,
    pub target_utilization: f64,
    pub minimum_budget_ratio: f64,
    pub ema_alpha: f64,
    pub batches_observed: u64,
    pub deep_cost_ema_us: f64,
    pub utilization_ema: f64,
    pub last_queue_pressure: f64,
    pub last_effective_budget_us: f64,
    pub minimum_effective_budget_us: f64,
    pub maximum_effective_budget_us: f64,
    pub last_planned_deep_cost_us: f64,
    pub last_actual_deep_cost_us: f64,
    pub pressure_limited_batches: u64,
    pub actual_budget_overrun_batches: u64,
}

pub struct BudgetScheduler {
    configured_budget_us: f64,
    safety_ratio: f64,
    target_utilization: f64,
    minimum_budget_ratio: f64,
    ema_alpha: f64,
    deep_cost_ema_us: f64,
    utilization_ema: f64,
    batches_observed: u64,
    last_queue_pressure: f64,
    last_effective_budget_us: f64,
    minimum_effective_budget_us: f64,
    maximum_effective_budget_us: f64,
    last_planned_deep_cost_us: f64,
    last_actual_deep_cost_us: f64,
    pressure_limited_batches: u64,
    actual_budget_overrun_batches: u64,
}

impl BudgetScheduler {
    pub fn new(configured_budget_us: f64, safety_ratio: f64) -> Self {
        Self::with_adaptive_feedback(
            configured_budget_us,
            safety_ratio,
            0.80,
            0.25_f64.min(safety_ratio),
            0.20,
        )
        .expect("default adaptive budget configuration must be valid")
    }

    pub fn with_adaptive_feedback(
        configured_budget_us: f64,
        safety_ratio: f64,
        target_utilization: f64,
        minimum_budget_ratio: f64,
        ema_alpha: f64,
    ) -> Result<Self, String> {
        if !configured_budget_us.is_finite() || configured_budget_us <= 0.0 {
            return Err("configured budget must be finite and positive".to_string());
        }
        if !safety_ratio.is_finite() || !(0.0..=1.0).contains(&safety_ratio) || safety_ratio == 0.0 {
            return Err("safety ratio must be in (0, 1]".to_string());
        }
        if !target_utilization.is_finite()
            || !(0.0..=1.0).contains(&target_utilization)
            || target_utilization == 0.0
        {
            return Err("target utilization must be in (0, 1]".to_string());
        }
        if !minimum_budget_ratio.is_finite()
            || minimum_budget_ratio <= 0.0
            || minimum_budget_ratio > safety_ratio
        {
            return Err("minimum budget ratio must be in (0, safety ratio]".to_string());
        }
        if !ema_alpha.is_finite() || !(0.0..=1.0).contains(&ema_alpha) || ema_alpha == 0.0 {
            return Err("EMA alpha must be in (0, 1]".to_string());
        }
        let initial_effective_budget_us = configured_budget_us * safety_ratio;
        Ok(Self {
            configured_budget_us,
            safety_ratio,
            target_utilization,
            minimum_budget_ratio,
            ema_alpha,
            deep_cost_ema_us: 40.0,
            utilization_ema: target_utilization,
            batches_observed: 0,
            last_queue_pressure: 0.0,
            last_effective_budget_us: initial_effective_budget_us,
            minimum_effective_budget_us: initial_effective_budget_us,
            maximum_effective_budget_us: initial_effective_budget_us,
            last_planned_deep_cost_us: 0.0,
            last_actual_deep_cost_us: 0.0,
            pressure_limited_batches: 0,
            actual_budget_overrun_batches: 0,
        })
    }

    pub fn schedule(
        &mut self,
        flows: Vec<ClosedFlow>,
        metrics: &RuntimeMetrics,
    ) -> Vec<ScheduledFlow> {
        self.schedule_with_pressure(flows, metrics, 0.0)
    }

    pub fn schedule_with_pressure(
        &mut self,
        flows: Vec<ClosedFlow>,
        metrics: &RuntimeMetrics,
        queue_pressure: f64,
    ) -> Vec<ScheduledFlow> {
        let key_flow_count = flows.iter().filter(|flow| flow.is_key_flow).count() as u64;
        metrics
            .key_flows_total
            .fetch_add(key_flow_count, Ordering::Relaxed);
        metrics
            .key_flows_base_materialized
            .fetch_add(key_flow_count, Ordering::Relaxed);
        let mut order: Vec<usize> = (0..flows.len()).collect();
        order.sort_by(|left, right| {
            flows[*right]
                .is_key_flow
                .cmp(&flows[*left].is_key_flow)
                .then_with(|| flows[*right].priority.total_cmp(&flows[*left].priority))
                .then_with(|| flows[*left].flow_id.cmp(&flows[*right].flow_id))
        });
        let queue_pressure = if queue_pressure.is_finite() {
            queue_pressure.max(0.0)
        } else {
            2.0
        };
        let pressure = self.utilization_ema.max(queue_pressure).max(0.05);
        let unconstrained_ratio = self.target_utilization / pressure;
        let budget_ratio = unconstrained_ratio
            .max(self.minimum_budget_ratio)
            .min(self.safety_ratio);
        let effective_budget = self.configured_budget_us * budget_ratio;
        if budget_ratio + f64::EPSILON < self.safety_ratio {
            self.pressure_limited_batches = self.pressure_limited_batches.saturating_add(1);
        }
        self.last_queue_pressure = queue_pressure;
        self.last_effective_budget_us = effective_budget;
        self.minimum_effective_budget_us = self.minimum_effective_budget_us.min(effective_budget);
        self.maximum_effective_budget_us = self.maximum_effective_budget_us.max(effective_budget);
        let mut deep = vec![false; flows.len()];
        let mut used = 0.0;
        for index in order {
            if used + self.deep_cost_ema_us <= effective_budget {
                deep[index] = true;
                used += self.deep_cost_ema_us;
            }
        }
        let deep_selected = deep.iter().filter(|selected| **selected).count() as u64;
        let deep_deferred = flows.len() as u64 - deep_selected;
        let key_deep_selected = flows
            .iter()
            .zip(&deep)
            .filter(|(flow, selected)| flow.is_key_flow && **selected)
            .count() as u64;
        metrics
            .deep_flows_selected
            .fetch_add(deep_selected, Ordering::Relaxed);
        metrics
            .deep_flows_deferred
            .fetch_add(deep_deferred, Ordering::Relaxed);
        metrics
            .key_flows_deep_selected
            .fetch_add(key_deep_selected, Ordering::Relaxed);
        metrics.record_key_schedule(key_flow_count, key_deep_selected);

        let mut actual_deep_cost_us = 0.0;
        let scheduled = flows
            .into_iter()
            .enumerate()
            .map(|(index, flow)| {
                if deep[index] {
                    let started = Instant::now();
                    let scheduled = flow.into_scheduled(true);
                    actual_deep_cost_us += started.elapsed().as_secs_f64() * 1_000_000.0;
                    scheduled
                } else {
                    flow.into_scheduled(false)
                }
            })
            .collect();
        let utilization_sample = queue_pressure.max(
            actual_deep_cost_us / self.configured_budget_us.max(f64::MIN_POSITIVE),
        );
        if deep_selected > 0 {
            let measured_per_flow = (actual_deep_cost_us / deep_selected as f64).max(0.001);
            self.deep_cost_ema_us = (1.0 - self.ema_alpha) * self.deep_cost_ema_us
                + self.ema_alpha * measured_per_flow;
        }
        self.utilization_ema = (1.0 - self.ema_alpha) * self.utilization_ema
            + self.ema_alpha * utilization_sample.max(0.05);
        self.batches_observed = self.batches_observed.saturating_add(1);
        self.last_planned_deep_cost_us = used;
        self.last_actual_deep_cost_us = actual_deep_cost_us;
        metrics.observe_budget_cost(used, actual_deep_cost_us);
        if actual_deep_cost_us > self.configured_budget_us {
            metrics.budget_overrun_count.fetch_add(1, Ordering::Relaxed);
            self.actual_budget_overrun_batches = self.actual_budget_overrun_batches.saturating_add(1);
        }
        scheduled
    }

    pub fn snapshot(&self) -> AdaptiveBudgetSnapshot {
        AdaptiveBudgetSnapshot {
            schema_version: 1,
            strategy: "ema_cost_queue_pressure_marginal_utility_v1",
            configured_budget_us: self.configured_budget_us,
            safety_ratio: self.safety_ratio,
            target_utilization: self.target_utilization,
            minimum_budget_ratio: self.minimum_budget_ratio,
            ema_alpha: self.ema_alpha,
            batches_observed: self.batches_observed,
            deep_cost_ema_us: self.deep_cost_ema_us,
            utilization_ema: self.utilization_ema,
            last_queue_pressure: self.last_queue_pressure,
            last_effective_budget_us: self.last_effective_budget_us,
            minimum_effective_budget_us: self.minimum_effective_budget_us,
            maximum_effective_budget_us: self.maximum_effective_budget_us,
            last_planned_deep_cost_us: self.last_planned_deep_cost_us,
            last_actual_deep_cost_us: self.last_actual_deep_cost_us,
            pressure_limited_batches: self.pressure_limited_batches,
            actual_budget_overrun_batches: self.actual_budget_overrun_batches,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::flow::test_closed_flow;

    #[test]
    fn equal_priority_deep_budget_uses_stable_flow_id_tiebreak() {
        let mut scheduler = BudgetScheduler::new(40.0, 1.0);
        let metrics = RuntimeMetrics::default();
        let scheduled = scheduler.schedule(
            vec![
                test_closed_flow("flow-z", false, 1.0),
                test_closed_flow("flow-a", false, 1.0),
                test_closed_flow("flow-m", false, 1.0),
            ],
            &metrics,
        );
        let deep_ids: Vec<&str> = scheduled
            .iter()
            .filter(|flow| flow.features[37] == 1.0)
            .map(|flow| flow.flow_id.as_str())
            .collect();

        assert_eq!(deep_ids, vec!["flow-a"]);
        assert_eq!(metrics.deep_flows_selected.load(Ordering::Relaxed), 1);
        assert_eq!(metrics.deep_flows_deferred.load(Ordering::Relaxed), 2);
    }

    #[test]
    fn key_flow_stages_are_counted_before_remote_delivery() {
        let mut scheduler = BudgetScheduler::new(40.0, 1.0);
        let metrics = RuntimeMetrics::default();
        let scheduled = scheduler.schedule(
            vec![
                test_closed_flow("key", true, 1.0),
                test_closed_flow("normal", false, 100.0),
            ],
            &metrics,
        );

        assert_eq!(scheduled.len(), 2);
        assert_eq!(metrics.key_flows_total.load(Ordering::Relaxed), 1);
        assert_eq!(
            metrics.key_flows_base_materialized.load(Ordering::Relaxed),
            1
        );
        assert_eq!(metrics.key_flows_deep_selected.load(Ordering::Relaxed), 1);
    }

    #[test]
    fn queue_pressure_shrinks_optional_deep_budget_and_is_auditable() {
        let mut scheduler = BudgetScheduler::with_adaptive_feedback(400.0, 1.0, 0.80, 0.25, 0.50)
            .expect("valid adaptive scheduler");
        let metrics = RuntimeMetrics::default();
        let scheduled = scheduler.schedule_with_pressure(
            (0..10)
                .map(|index| test_closed_flow(&format!("flow-{index:02}"), false, 1.0))
                .collect(),
            &metrics,
            2.0,
        );
        let deep = scheduled
            .iter()
            .filter(|flow| flow.features[37] == 1.0)
            .count();
        let snapshot = scheduler.snapshot();

        assert_eq!(deep, 4);
        assert_eq!(snapshot.batches_observed, 1);
        assert_eq!(snapshot.pressure_limited_batches, 1);
        assert!((snapshot.last_effective_budget_us - 160.0).abs() < 1e-9);
        assert!(snapshot.deep_cost_ema_us > 0.0);
    }

    #[test]
    fn adaptive_configuration_rejects_an_unreachable_minimum_ratio() {
        let error = BudgetScheduler::with_adaptive_feedback(100.0, 0.5, 0.8, 0.75, 0.2)
            .err()
            .expect("invalid minimum ratio must fail");
        assert!(error.contains("minimum budget ratio"));
    }
}
