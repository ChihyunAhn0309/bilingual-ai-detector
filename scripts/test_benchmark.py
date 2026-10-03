import unittest
from benchmark_epoch import public_counts, select_sample, paired_metrics


class BenchmarkTests(unittest.TestCase):
    def test_strict_mixed_is_error_for_both_pure_classes(self):
        rows = [{"condition": c, "pangram_pred": "Mixed", "gptzero_pred": "mixed", "originality_pred": "human"}
                for c in ("human", "vanilla", "style_transfer")]
        result = public_counts(rows)
        self.assertEqual(result["gptzero"]["human"]["errors"], 1)
        self.assertEqual(result["gptzero"]["vanilla"]["errors"], 1)
        self.assertEqual(result["originality"]["human"]["errors"], 0)

    def test_selection_pairs_author_and_generation_model(self):
        rows = []
        for genre in ("blog", "fiction", "scientific"):
            for author in range(8):
                for condition in ("human", "vanilla", "style_transfer"):
                    for unit in (["snippet_1", "snippet_2"] if condition == "human" else ["claude", "gemini", "gpt"]):
                        rows.append({"genre": genre, "author_key": str(author), "condition": condition, "unit": unit})
        result = select_sample(rows)
        self.assertEqual(result, select_sample(rows))
        self.assertEqual(len(result), 36)
        for i in range(0, 36, 3):
            trio = result[i:i+3]
            self.assertEqual(len({r["author_key"] for r in trio}), 1)
            self.assertEqual(trio[1]["unit"], trio[2]["unit"])

    def test_failed_local_result_is_not_human_and_coverage_is_visible(self):
        rows = [{"condition": "human", "local": False}, {"condition": "vanilla", "local": True},
                {"condition": "style_transfer", "local_error": "unavailable"}]
        result = paired_metrics(rows, "local")
        self.assertEqual(result["completed"], 2)
        self.assertEqual(result["requested"], 3)
        self.assertEqual(result["accuracy_on_completed"], 1)
        self.assertIsNone(result["style_transfer"]["rate"])


if __name__ == "__main__":
    unittest.main()
