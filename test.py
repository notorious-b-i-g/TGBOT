def solve_elections(t, data):
    results = []
    for test in range(t):
        n, c = data[test][0]
        a = data[test][1]

        test_result = []

        for i in range(n):
            needed_exclusions = 0
            current_votes = a[i] + c

            other_candidates = sorted(a[:i] + a[i + 1:])

            for fans in other_candidates:
                if fans >= current_votes:
                    needed_exclusions += 1
                    current_votes += fans

            test_result.append(needed_exclusions)

        results.append(test_result)

    return results


def solve_elections(t, data):
    results = []
    for test in range(t):
        n, c = data[test][0]
        a = data[test][1]

        test_result = []

        for i in range(n):
            needed_exclusions = 0
            current_votes = a[i] + c

            other_candidates = sorted([(a[j], j) for j in range(n) if j != i], key=lambda x: x[0])

            for fans, idx in other_candidates:
                if fans >= current_votes:
                    needed_exclusions += 1
                    current_votes += fans
                else:
                    break

            test_result.append(needed_exclusions)

        results.append(test_result)

    return results

