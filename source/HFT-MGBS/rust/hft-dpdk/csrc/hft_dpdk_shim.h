#ifndef HFT_DPDK_SHIM_H
#define HFT_DPDK_SHIM_H

#include <stddef.h>
#include <stdint.h>

struct hft_dpdk_stats {
    uint64_t ipackets;
    uint64_t ibytes;
    uint64_t imissed;
    uint64_t ierrors;
    uint64_t rx_nombuf;
    uint64_t opackets;
    uint64_t obytes;
    uint64_t oerrors;
};

enum hft_dpdk_traffic_profile {
    HFT_DPDK_TRAFFIC_PROFILE_UDP_COMPAT = 0,
    HFT_DPDK_TRAFFIC_PROFILE_STOCK_TCP_RSS_DIAGNOSTIC = 1,
    HFT_DPDK_TRAFFIC_PROFILE_FULL_PIPELINE = 2,
};

int hft_dpdk_eal_init(int argc, char **argv);
int hft_dpdk_eal_cleanup(void);
int hft_dpdk_thread_register(void);
void hft_dpdk_thread_unregister(void);
uint16_t hft_dpdk_port_count(void);
int hft_dpdk_find_port(const char *name, uint16_t *port_id);
int hft_dpdk_port_init(uint16_t port_id, void *mempool, uint16_t rx_desc,
                       uint16_t tx_desc, uint16_t queue_count,
                       uint32_t traffic_profile,
                       uint16_t *actual_rx_desc,
                       uint16_t *actual_tx_desc);
int hft_dpdk_port_mac(uint16_t port_id, uint8_t mac[6]);
int hft_dpdk_port_link(uint16_t port_id, uint32_t *speed_mbps, uint8_t *up);
int hft_dpdk_port_stats(uint16_t port_id, struct hft_dpdk_stats *stats);
void hft_dpdk_port_stop_close(uint16_t port_id);
void *hft_dpdk_mempool_create(const char *name, uint32_t count,
                              uint32_t cache_size, int socket_id);
void hft_dpdk_mempool_free(void *mempool);
int hft_dpdk_mempool_counts(void *mempool, uint32_t *available,
                            uint32_t *in_use);
int hft_dpdk_socket_id(void);
uint64_t hft_dpdk_tsc_hz(void);
uint64_t hft_dpdk_rdtsc(void);
int hft_dpdk_prepare_synthetic_burst(
    void *mempool, void **packets, uint16_t count, const uint8_t *templates,
    uint16_t template_count, uint16_t frame_size, uint64_t sequence,
    uint64_t timestamp_cycles, uint16_t timestamp_offset);
uint16_t hft_dpdk_tx_burst(uint16_t port_id, uint16_t queue_id, void **packets,
                           uint16_t count);
uint16_t hft_dpdk_rx_burst(uint16_t port_id, uint16_t queue_id, void **packets,
                           uint16_t capacity);
int hft_dpdk_packet_view(void *packet, const uint8_t **data,
                         uint32_t *length);
uint64_t hft_dpdk_burst_bytes(void **packets, uint16_t count);
uint64_t hft_dpdk_first_timestamp(void **packets, uint16_t count,
                                  uint16_t timestamp_offset);
void hft_dpdk_free_burst(void **packets, uint16_t count);
void hft_dpdk_free_burst_from(void **packets, uint16_t start, uint16_t count);

#endif
