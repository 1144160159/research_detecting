#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_endian.h>

struct {
    __uint(type, BPF_MAP_TYPE_XSKMAP);
    __uint(max_entries, 64);
    __type(key, __u32);
    __type(value, __u32);
} XSKS_MAP SEC(".maps");

SEC("xdp")
int xdp_redirect(struct xdp_md *ctx)
{
    void *data;
    void *data_meta;
    __u64 timestamp_ns;
    __u32 queue_id;

    if (bpf_xdp_adjust_meta(ctx, -(int)sizeof(timestamp_ns)) < 0)
        return XDP_PASS;

    data = (void *)(long)ctx->data;
    data_meta = (void *)(long)ctx->data_meta;
    if (data_meta + sizeof(timestamp_ns) > data)
        return XDP_ABORTED;

    timestamp_ns = bpf_ktime_get_ns();
    __builtin_memcpy(data_meta, &timestamp_ns, sizeof(timestamp_ns));
    queue_id = ctx->rx_queue_index;
    return bpf_redirect_map(&XSKS_MAP, queue_id, XDP_PASS);
}

char LICENSE[] SEC("license") = "GPL";
