import os
import shutil
import tempfile
import unittest

from enginecheck import GameAnalyzer


def _touch(base, *paths):
    for path in paths:
        full = os.path.join(base, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, "a", encoding="utf-8").close()


class TestGameAnalyzer(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def analyze(self, *paths):
        _touch(self.temp_dir, *paths)
        analyzer = GameAnalyzer(self.temp_dir)
        self.assertTrue(analyzer.scan_files())
        return analyzer

    def test_rpg_maker_xp(self):
        analyzer = self.analyze("game.ini")
        self.assertEqual(analyzer.detected_engine, "RPG Maker (XP/VX/VX Ace)")

    def test_rpg_maker_mv_rpgmvp(self):
        analyzer = self.analyze("img/test.rpgmvp")
        self.assertEqual(analyzer.detected_engine, "RPG Maker (MV/MZ / NW.js)")

    def test_rpg_maker_mv_nwjs(self):
        analyzer = self.analyze("package.json", "nw.dll")
        self.assertEqual(analyzer.detected_engine, "RPG Maker (MV/MZ / NW.js)")

    def test_rpg_maker_mv_with_webview_paks(self):
        analyzer = self.analyze("package.json", "nw.dll", "paks/nw_100_percent.pak")
        self.assertEqual(analyzer.detected_engine, "RPG Maker (MV/MZ / NW.js)")

    def test_pubcoder_nwjs_runtime(self):
        """PubCoder NW.js 배포 — 파일명에 pubcoder 없음, exe 바이너리에 pubcoder 문자열"""
        _touch(self.temp_dir, "nw.dll", "nw_100_percent.pak", "nw_200_percent.pak", "resources.pak")
        exe_path = os.path.join(self.temp_dir, "photobook.exe")
        with open(exe_path, "wb") as handle:
            handle.write(b"\x00" * 64 + b"pubcoder" + b"XPUB")
        analyzer = GameAnalyzer(self.temp_dir)
        self.assertTrue(analyzer.scan_files())
        self.assertEqual(analyzer.detected_engine, "PubCoder (Interactive Ebook/App)")

    def test_pubcoder(self):
        analyzer = self.analyze("pubcoder.exe")
        self.assertEqual(analyzer.detected_engine, "PubCoder (Interactive Ebook/App)")

    def test_nw_webview_pak_not_unreal(self):
        _touch(self.temp_dir, "paks/nw_100_percent.pak")
        analyzer = GameAnalyzer(self.temp_dir)
        self.assertFalse(analyzer.scan_files())

    def test_electron_chrome_paks(self):
        analyzer = self.analyze(
            "chrome_100_percent.pak",
            "chrome_200_percent.pak",
            "resources.pak",
            "resources/app.asar",
        )
        self.assertEqual(analyzer.detected_engine, "Electron (Chromium App)")

    def test_electron_locales_not_unreal(self):
        _touch(self.temp_dir, "chrome_100_percent.pak", "chrome_200_percent.pak", "locales/ko.pak", "locales/en-us.pak")
        analyzer = GameAnalyzer(self.temp_dir)
        self.assertTrue(analyzer.scan_files())
        self.assertEqual(analyzer.detected_engine, "Electron (Chromium App)")

    def test_unreal_pak(self):
        analyzer = self.analyze("paks/foo.pak")
        self.assertEqual(analyzer.detected_engine, "Unreal Engine")

    def test_unreal_binaries_engine(self):
        analyzer = self.analyze("Binaries/Win64/x", "Engine/y")
        self.assertEqual(analyzer.detected_engine, "Unreal Engine")

    def test_unity_data_folder(self):
        analyzer = self.analyze("game_Data/Managed/x")
        self.assertEqual(analyzer.detected_engine, "Unity Engine")

    def test_unity_dll(self):
        analyzer = self.analyze("unityplayer.dll")
        self.assertEqual(analyzer.detected_engine, "Unity Engine")

    def test_clickteam_fusion_modules(self):
        analyzer = self.analyze("Modules/mmf2d3d8.dll", "Modules/kcmouse.mfx", "Modules/mmfs2.dll")
        self.assertEqual(analyzer.detected_engine, "Clickteam Fusion")


if __name__ == "__main__":
    unittest.main()
