from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable

from osint_core import collect_osint


def run_batch(
    targets: Iterable[str],
    workers: int = 5,
    timeout: int = 12,
    user_agent: str = "OSINT-Recon-Dual-Mode/1.0",
    verify_tls: bool = True,
    with_subdomains: bool = True,
):
    clean_targets = [t.strip() for t in targets if t and t.strip()]
    results = []

    with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        fut_map = {
            ex.submit(
                collect_osint,
                t,
                timeout=timeout,
                user_agent=user_agent,
                verify_tls=verify_tls,
                with_subdomains=with_subdomains,
            ): t
            for t in clean_targets
        }

        for fut in as_completed(fut_map):
            t = fut_map[fut]
            try:
                r = fut.result()
            except Exception as e:
                r = {
                    "target_input": t,
                    "normalized": t,
                    "errors": [f"batch_error: {e}"],
                }
            results.append(r)

    # keep output stable by input order
    order = {t: i for i, t in enumerate(clean_targets)}
    results.sort(key=lambda x: order.get(x.get("target_input", ""), 10**9))
    return results
