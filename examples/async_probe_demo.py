import asyncio
import time

from app.services.probe import simulate_device_probe


async def main() -> None:
    device_ids = ["RTR-101", "SW-102", "SRV-103"]

    started = time.perf_counter()
    sequential_results = []
    for device_id in device_ids:
        sequential_results.append(
            await simulate_device_probe(device_id)
        )
    sequential_elapsed = time.perf_counter() - started

    started = time.perf_counter()
    concurrent_results = await asyncio.gather(
        *(simulate_device_probe(device_id) for device_id in device_ids)
    )
    concurrent_elapsed = time.perf_counter() - started

    print("Sequential results:", sequential_results)
    print(f"Sequential elapsed: {sequential_elapsed:.3f} seconds")
    print("Concurrent results:", list(concurrent_results))
    print(f"Concurrent elapsed: {concurrent_elapsed:.3f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
