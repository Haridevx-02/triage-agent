import unittest

from rag_service import retrieve_knowledge


class RAGServiceTests(unittest.TestCase):
    def test_prior_auth_retrieval(self):
        hits = retrieve_knowledge("urgent MRI needs prior authorization and care approval", top_k=3)
        self.assertTrue(hits)
        self.assertTrue(any("Prior Authorization" in hit or "prior authorization" in hit.lower() for hit in hits))

    def test_claim_denial_retrieval(self):
        hits = retrieve_knowledge("claim was denied because prior auth missing", top_k=3)
        self.assertTrue(hits)
        self.assertTrue(any("Claim Denial" in hit or "claim" in hit.lower() for hit in hits))


if __name__ == "__main__":
    unittest.main()
