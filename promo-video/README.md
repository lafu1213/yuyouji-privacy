# 語遊記 宣傳影片

- `yuyouji-promo.mp4`：成品，1080×1920 直式、32 秒、含配樂（適用 IG Reels / YouTube Shorts / TikTok）
- `promo.html`：動畫原始檔，直接用瀏覽器開啟即可循環預覽
- `music.py`：合成配樂（無版權疑慮）
- `render.mjs`：用 Playwright 逐格擷取並以 ffmpeg 輸出 MP4

## 重新輸出

```sh
npm pack @fontsource/noto-sans-tc @fontsource/noto-serif-tc   # 解壓到 fonts/noto-sans-tc、fonts/noto-serif-tc
python3 music.py
node render.mjs                     # 輸出 yuyouji-promo.mp4
node render.mjs --still 10,15       # 只輸出指定秒數的截圖
```

## 分鏡

| 秒數 | 內容 |
|---|---|
| 0–4 | 開場提問：孩子背成語，總是背了又忘？→ 換個方式，讓成語變好玩！ |
| 4–8 | 品牌登場：語遊記・國小成語學習好夥伴 |
| 8–13 | 緊扣課本：翰林・南一・康軒，一到六年級 |
| 13–17.5 | AI 成語小故事（守株待兔） |
| 17.5–22 | 趣味測驗＋錯題本 |
| 22–26 | 朗讀＋連續學習天數 |
| 26–29 | 免註冊・無廣告・資料只存本機・全家共用 |
| 29–32 | 結尾：App Store 搜尋「語遊記」 |
