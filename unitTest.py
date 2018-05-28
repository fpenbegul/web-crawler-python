import WebCrawler
import unittest

class TestesWebCrawler(unittest.TestCase):
    def test_abrirConexaoCloud(self):
        conn, cur, status = WebCrawler.abrirConexaoCloud()
        self.assertEqual(status, "Ok")
        self.assertIsNot(status, "nOk")

    def test_criaBase(self):
        conn, cur, status = WebCrawler.abrirConexaoCloud()
        self.assertTrue(WebCrawler.criaBase("teste", conn, cur))

    def test_fechaConexao(self):
        conn, cur, status = WebCrawler.abrirConexaoCloud()
        self.assertTrue(WebCrawler.fechaConexao(conn, cur, status))

if __name__ == '__main__':
    unittest.main()