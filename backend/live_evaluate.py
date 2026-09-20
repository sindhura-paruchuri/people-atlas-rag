import asyncio
import json
import os
from datetime import datetime, UTC

import httpx


API_URL = "http://localhost:8000"

TEST_CASES = [
    {
        "name": "Database retrieval",
        "query": "Tell me about Peggy Seeger",
        "allow_web": True,
        "expected": "database",
    },
    {
        "name": "Web fallback",
        "query": "What are the latest announcements from NASA?",
        "allow_web": True,
        "expected": "web",
    },
    {
        "name": "Web disabled",
        "query": "What are the latest announcements from NASA?",
        "allow_web": False,
        "expected": "no_web",
    },
]


async def run_test(client, case):
    response = await client.post(
        f"{API_URL}/query",
        headers={
            "Authorization":
                f"Bearer {os.environ['RAG_API_TOKEN']}"
        },
        json={
            "query": case["query"],
            "allow_web": case["allow_web"],
        },
    )

    result = response.json()

    trace = result.get("trace", [])
    sources = result.get("sources", [])

    research_status = ""

    for item in trace:
        if item.get("agent") == "Web research":
            research_status = item.get("status", "")

    if "Not needed" in research_status:
        actual_route = "database"

    elif (
        "using" in research_status.lower()
        or "added" in research_status.lower()
    ):
        actual_route = "web"

    elif "disabled" in research_status.lower():
        actual_route = "no_web"

    else:
        actual_route = "unknown"

    route_correct = actual_route == case["expected"]

    return {
        "name": case["name"],
        "query": case["query"],
        "status_code": response.status_code,
        "expected_route": case["expected"],
        "actual_route": actual_route,
        "route_correct": route_correct,
        "citation_valid": result.get("citation_valid"),
        "source_count": len(sources),
        "latency_ms": result.get("latency_ms"),
        "usage": result.get("usage", {}),
        "trace": trace,
    }


async def main():
    results = []

    async with httpx.AsyncClient(timeout=90) as client:
        for case in TEST_CASES:
            print(f"\nRunning: {case['name']}")

            try:
                result = await run_test(client, case)
                results.append(result)

                print(
                    f"Status: {result['status_code']}"
                )
                print(
                    f"Expected route: "
                    f"{result['expected_route']}"
                )
                print(
                    f"Actual route: "
                    f"{result['actual_route']}"
                )
                print(
                    f"Route correct: "
                    f"{result['route_correct']}"
                )
                print(
                    f"Citation valid: "
                    f"{result['citation_valid']}"
                )
                print(
                    f"Sources: "
                    f"{result['source_count']}"
                )
                print(
                    f"Latency: "
                    f"{result['latency_ms']} ms"
                )

            except Exception as exc:
                results.append({
                    "name": case["name"],
                    "query": case["query"],
                    "error": str(exc),
                })

                print(f"ERROR: {exc}")

    successful = [
        r for r in results
        if r.get("status_code") == 200
    ]

    correct_routes = [
        r for r in successful
        if r.get("route_correct")
    ]

    cited = [
        r for r in successful
        if r.get("citation_valid") is True
    ]

    latencies = [
        r["latency_ms"]
        for r in successful
        if isinstance(r.get("latency_ms"), (int, float))
    ]

    summary = {
        "timestamp": datetime.now(UTC).isoformat(),
        "total_tests": len(results),
        "successful_requests": len(successful),
        "route_accuracy": (
            len(correct_routes) / len(results)
            if results
            else 0
        ),
        "citation_valid_rate": (
            len(cited) / len(successful)
            if successful
            else 0
        ),
        "average_latency_ms": (
            sum(latencies) / len(latencies)
            if latencies
            else None
        ),
    }

    output = {
        "summary": summary,
        "results": results,
    }

    with open(
        "live_eval_results.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            output,
            f,
            indent=2,
        )

    print("\n==============================")
    print("LIVE EVALUATION SUMMARY")
    print("==============================")

    print(
        f"Successful requests: "
        f"{summary['successful_requests']}/"
        f"{summary['total_tests']}"
    )

    print(
        f"Routing accuracy: "
        f"{summary['route_accuracy']:.0%}"
    )

    print(
        f"Citation-valid rate: "
        f"{summary['citation_valid_rate']:.0%}"
    )

    print(
        f"Average latency: "
        f"{summary['average_latency_ms']:.0f} ms"
        if summary["average_latency_ms"] is not None
        else "Average latency: N/A"
    )

    print(
        "\nDetailed results saved to "
        "live_eval_results.json"
    )


if __name__ == "__main__":
    asyncio.run(main())