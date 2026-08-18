#define _GNU_SOURCE
#include "hft_dpdk_shim.h"

#include <errno.h>
#include <string.h>
#include <sys/types.h>

#include <rte_cycles.h>
#include <rte_eal.h>
#include <rte_ethdev.h>
#include <rte_lcore.h>
#include <rte_mbuf.h>
#include <rte_mempool.h>

int hft_dpdk_eal_init(int argc, char **argv) { return rte_eal_init(argc, argv); }

int hft_dpdk_eal_cleanup(void) { return rte_eal_cleanup(); }

int hft_dpdk_thread_register(void) { return rte_thread_register(); }

void hft_dpdk_thread_unregister(void) { rte_thread_unregister(); }

uint16_t hft_dpdk_port_count(void) { return rte_eth_dev_count_avail(); }

int hft_dpdk_find_port(const char *name, uint16_t *port_id) {
    return rte_eth_dev_get_port_by_name(name, port_id);
}

void *hft_dpdk_mempool_create(const char *name, uint32_t count,
                              uint32_t cache_size, int socket_id) {
    return rte_pktmbuf_pool_create(name, count, cache_size, 0,
                                   RTE_MBUF_DEFAULT_BUF_SIZE, socket_id);
}

void hft_dpdk_mempool_free(void *mempool) {
    if (mempool != NULL)
        rte_mempool_free((struct rte_mempool *)mempool);
}

int hft_dpdk_mempool_counts(void *mempool, uint32_t *available,
                            uint32_t *in_use) {
    if (mempool == NULL || available == NULL || in_use == NULL)
        return -EINVAL;
    *available = rte_mempool_avail_count((struct rte_mempool *)mempool);
    *in_use = rte_mempool_in_use_count((struct rte_mempool *)mempool);
    return 0;
}

int hft_dpdk_socket_id(void) { return rte_socket_id(); }

int hft_dpdk_port_mac(uint16_t port_id, uint8_t mac[6]) {
    struct rte_ether_addr address;
    int status = rte_eth_macaddr_get(port_id, &address);
    if (status != 0)
        return status;
    memcpy(mac, address.addr_bytes, RTE_ETHER_ADDR_LEN);
    return 0;
}

int hft_dpdk_port_init(uint16_t port_id, void *mempool, uint16_t rx_desc,
                       uint16_t tx_desc, uint16_t queue_count,
                       uint32_t traffic_profile,
                       uint16_t *actual_rx_desc,
                       uint16_t *actual_tx_desc) {
    struct rte_eth_dev_info info;
    struct rte_eth_conf config;
    struct rte_eth_rxconf rx_config;
    struct rte_eth_txconf tx_config;
    int socket_id;
    int status;
    uint16_t queue_id;

    if (actual_rx_desc == NULL || actual_tx_desc == NULL)
        return -EINVAL;
    memset(&info, 0, sizeof(info));
    status = rte_eth_dev_info_get(port_id, &info);
    if (status != 0)
        return status;
    if (queue_count == 0 || queue_count > info.max_rx_queues ||
        queue_count > info.max_tx_queues)
        return -EINVAL;
    if (traffic_profile != HFT_DPDK_TRAFFIC_PROFILE_UDP_COMPAT &&
        traffic_profile !=
            HFT_DPDK_TRAFFIC_PROFILE_STOCK_TCP_RSS_DIAGNOSTIC &&
        traffic_profile != HFT_DPDK_TRAFFIC_PROFILE_FULL_PIPELINE)
        return -EINVAL;
    if (traffic_profile ==
            HFT_DPDK_TRAFFIC_PROFILE_STOCK_TCP_RSS_DIAGNOSTIC &&
        queue_count < 2)
        return -EINVAL;
    memset(&config, 0, sizeof(config));
    if (traffic_profile ==
        HFT_DPDK_TRAFFIC_PROFILE_STOCK_TCP_RSS_DIAGNOSTIC) {
        /*
         * Stock bnx2x advertises no ethdev RSS hash functions, but its PF
         * startup always installs IPv4/TCP RSS and the indirection table.
         * Keep the ethdev request empty so generic validation can pass; this
         * profile is diagnostic-only and must be proven by per-queue counts.
         */
        config.rxmode.mq_mode = RTE_ETH_MQ_RX_NONE;
        config.rx_adv_conf.rss_conf.rss_hf = 0;
    } else if (traffic_profile == HFT_DPDK_TRAFFIC_PROFILE_FULL_PIPELINE) {
        uint64_t requested_rss =
            RTE_ETH_RSS_NONFRAG_IPV4_TCP |
            RTE_ETH_RSS_NONFRAG_IPV4_UDP |
            RTE_ETH_RSS_NONFRAG_IPV6_TCP |
            RTE_ETH_RSS_NONFRAG_IPV6_UDP;
        uint64_t supported_rss = requested_rss & info.flow_type_rss_offloads;
        config.rxmode.mq_mode =
            queue_count > 1 ? RTE_ETH_MQ_RX_RSS : RTE_ETH_MQ_RX_NONE;
        config.rx_adv_conf.rss_conf.rss_hf =
            queue_count > 1 ? supported_rss : 0;
        if (queue_count > 1 && supported_rss == 0)
            return -ENOTSUP;
    } else {
        config.rxmode.mq_mode =
            queue_count > 1 ? RTE_ETH_MQ_RX_RSS : RTE_ETH_MQ_RX_NONE;
        if (queue_count > 1)
            config.rx_adv_conf.rss_conf.rss_hf =
                RTE_ETH_RSS_NONFRAG_IPV4_UDP;
    }
    config.txmode.mq_mode = RTE_ETH_MQ_TX_NONE;
    status = rte_eth_dev_configure(port_id, queue_count, queue_count, &config);
    if (status != 0)
        return status;
    status = rte_eth_dev_adjust_nb_rx_tx_desc(port_id, &rx_desc, &tx_desc);
    if (status != 0)
        return status;
    *actual_rx_desc = rx_desc;
    *actual_tx_desc = tx_desc;
    socket_id = rte_eth_dev_socket_id(port_id);
    if (socket_id < 0)
        socket_id = rte_socket_id();
    rx_config = info.default_rxconf;
    rx_config.offloads = config.rxmode.offloads;
    tx_config = info.default_txconf;
    tx_config.offloads = config.txmode.offloads;
    for (queue_id = 0; queue_id < queue_count; queue_id++) {
        status = rte_eth_rx_queue_setup(port_id, queue_id, rx_desc, socket_id,
                                        &rx_config,
                                        (struct rte_mempool *)mempool);
        if (status != 0)
            return status;
        status = rte_eth_tx_queue_setup(port_id, queue_id, tx_desc, socket_id,
                                        &tx_config);
        if (status != 0)
            return status;
    }
    status = rte_eth_dev_start(port_id);
    if (status != 0)
        return status;
    status = rte_eth_promiscuous_enable(port_id);
    if (status != 0)
        return status;
    return 0;
}

int hft_dpdk_port_link(uint16_t port_id, uint32_t *speed_mbps, uint8_t *up) {
    struct rte_eth_link link;
    int status;
    memset(&link, 0, sizeof(link));
    status = rte_eth_link_get_nowait(port_id, &link);
    if (status != 0)
        return status;
    *speed_mbps = link.link_speed;
    *up = link.link_status;
    return 0;
}

int hft_dpdk_port_stats(uint16_t port_id, struct hft_dpdk_stats *output) {
    struct rte_eth_stats stats;
    int status;
    memset(&stats, 0, sizeof(stats));
    status = rte_eth_stats_get(port_id, &stats);
    if (status != 0)
        return status;
    output->ipackets = stats.ipackets;
    output->ibytes = stats.ibytes;
    output->imissed = stats.imissed;
    output->ierrors = stats.ierrors;
    output->rx_nombuf = stats.rx_nombuf;
    output->opackets = stats.opackets;
    output->obytes = stats.obytes;
    output->oerrors = stats.oerrors;
    return 0;
}

void hft_dpdk_port_stop_close(uint16_t port_id) {
    rte_eth_dev_stop(port_id);
    rte_eth_dev_close(port_id);
}

uint64_t hft_dpdk_tsc_hz(void) { return rte_get_tsc_hz(); }

uint64_t hft_dpdk_rdtsc(void) { return rte_rdtsc(); }

int hft_dpdk_prepare_synthetic_burst(
    void *mempool, void **packets, uint16_t count, const uint8_t *templates,
    uint16_t template_count, uint16_t frame_size, uint64_t sequence,
    uint64_t timestamp_cycles, uint16_t timestamp_offset) {
    struct rte_mbuf **mbufs = (struct rte_mbuf **)packets;
    uint16_t i;
    uint16_t template_mask;
    const int fixed_64_path =
        frame_size == 64 && template_count != 0 &&
        (template_count & (template_count - 1)) == 0;
    if (template_count == 0 || frame_size < 50 ||
        (uint32_t)timestamp_offset + sizeof(timestamp_cycles) > frame_size)
        return -EINVAL;
    template_mask = fixed_64_path ? (uint16_t)(template_count - 1) : 0;
    if (rte_pktmbuf_alloc_bulk((struct rte_mempool *)mempool, mbufs, count) != 0)
        return -ENOBUFS;
    for (i = 0; i < count; i++) {
        uint8_t *data = (uint8_t *)rte_pktmbuf_append(mbufs[i], frame_size);
        uint16_t template_index;
        if (data == NULL) {
            rte_pktmbuf_free_bulk(mbufs, count);
            return -EINVAL;
        }
        if (fixed_64_path) {
            template_index = (uint16_t)((sequence + i) & template_mask);
            memcpy(data, templates + ((size_t)template_index << 6), 64);
        } else {
            template_index =
                (uint16_t)((sequence + i) % template_count);
            memcpy(data, templates + (size_t)template_index * frame_size,
                   frame_size);
        }
        memcpy(data + timestamp_offset, &timestamp_cycles,
               sizeof(timestamp_cycles));
    }
    return 0;
}

uint16_t hft_dpdk_tx_burst(uint16_t port_id, uint16_t queue_id, void **packets,
                           uint16_t count) {
    return rte_eth_tx_burst(port_id, queue_id,
                            (struct rte_mbuf **)packets, count);
}

uint16_t hft_dpdk_rx_burst(uint16_t port_id, uint16_t queue_id, void **packets,
                           uint16_t capacity) {
    return rte_eth_rx_burst(port_id, queue_id,
                            (struct rte_mbuf **)packets, capacity);
}

int hft_dpdk_packet_view(void *packet, const uint8_t **data,
                         uint32_t *length) {
    struct rte_mbuf *mbuf = (struct rte_mbuf *)packet;
    if (mbuf == NULL || data == NULL || length == NULL)
        return -EINVAL;
    if (mbuf->nb_segs != 1 || rte_pktmbuf_pkt_len(mbuf) != rte_pktmbuf_data_len(mbuf))
        return -ENOTSUP;
    *data = rte_pktmbuf_mtod(mbuf, const uint8_t *);
    *length = rte_pktmbuf_data_len(mbuf);
    return 0;
}

uint64_t hft_dpdk_burst_bytes(void **packets, uint16_t count) {
    struct rte_mbuf **mbufs = (struct rte_mbuf **)packets;
    uint64_t bytes = 0;
    uint16_t i;
    for (i = 0; i < count; i++)
        bytes += rte_pktmbuf_pkt_len(mbufs[i]);
    return bytes;
}

uint64_t hft_dpdk_first_timestamp(void **packets, uint16_t count,
                                  uint16_t timestamp_offset) {
    struct rte_mbuf **mbufs = (struct rte_mbuf **)packets;
    uint64_t timestamp = 0;
    const uint8_t *data;
    if (count == 0 || rte_pktmbuf_pkt_len(mbufs[0]) <
                          (uint32_t)timestamp_offset + sizeof(timestamp))
        return 0;
    data = rte_pktmbuf_mtod_offset(mbufs[0], const uint8_t *,
                                   timestamp_offset);
    memcpy(&timestamp, data, sizeof(timestamp));
    return timestamp;
}

void hft_dpdk_free_burst(void **packets, uint16_t count) {
    rte_pktmbuf_free_bulk((struct rte_mbuf **)packets, count);
}

void hft_dpdk_free_burst_from(void **packets, uint16_t start, uint16_t count) {
    if (start < count)
        rte_pktmbuf_free_bulk(&((struct rte_mbuf **)packets)[start],
                              (uint16_t)(count - start));
}
