use std::env;
use std::fs;
use std::process::Command;

fn main() {
    println!("cargo:rerun-if-changed=csrc/hft_dpdk_shim.c");
    println!("cargo:rerun-if-changed=csrc/hft_dpdk_shim.h");
    let library = pkg_config::Config::new()
        .statik(true)
        .cargo_metadata(false)
        .probe("libdpdk")
        .expect("libdpdk.pc is required; run scripts/bootstrap_dpdk_bnx2x.sh");
    for link_path in &library.link_paths {
        let bnx2x_archive = link_path.join("librte_net_bnx2x.a");
        if bnx2x_archive.is_file() {
            println!("cargo:rerun-if-changed={}", bnx2x_archive.display());
            if let Some(install_root) = link_path.parent() {
                println!(
                    "cargo:rerun-if-changed={}",
                    install_root.join("hft-build-manifest.txt").display()
                );
            }
        }
    }
    let pkg_config = env::var_os("PKG_CONFIG").unwrap_or_else(|| "pkg-config".into());
    let link_flags = Command::new(pkg_config)
        .args(["--static", "--libs", "libdpdk"])
        .output()
        .expect("failed to execute pkg-config for the DPDK static linker flags");
    if !link_flags.status.success() {
        panic!(
            "pkg-config --static --libs libdpdk failed: {}",
            String::from_utf8_lossy(&link_flags.stderr)
        );
    }
    let response_path =
        std::path::PathBuf::from(env::var_os("OUT_DIR").expect("OUT_DIR is required"))
            .join("dpdk-linker.rsp");
    fs::write(&response_path, link_flags.stdout).expect("failed to write DPDK linker response");
    println!("cargo:rustc-link-arg=@{}", response_path.display());

    let mut build = cc::Build::new();
    build
        .file("csrc/hft_dpdk_shim.c")
        .flag_if_supported("-std=c11")
        .warnings(true);
    for include in library.include_paths {
        build.include(include);
    }
    build.compile("hft_dpdk_shim");
}
