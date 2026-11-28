# Tiêu chuẩn Kịch bản & Chỉ đạo Diễn xuất — Phim Ma Dân Gian / Kiếm Hiệp

> **Phiên bản:** `v2.0` (2026-11-28) · **Áp dụng cho:** mọi tập phim cốt truyện `ep*` (Phim Ma Dân Gian) và `kh*` (Kiếm Hiệp Cổ Trang).
> **Ai phải đọc:** mọi AI nhận vai `director`, `artist`, `animator`, `qa_critic`, `chief` — bất kể là model nào, phiên chat nào.
> **Nguồn gốc duy nhất (source of truth):** file này trong Git (`docs/roles/`) và bản sao công khai trên Hub `https://muse.alltool.pro/roles/`.

Tài liệu này mô tả **kết quả phải đạt**, không phụ thuộc AI cụ thể. AI mới tiếp nhận vai chỉ cần đọc file này + file vai của mình (`director.md`, `artist.md`, …) là làm tiếp được.

---

## 0. Phạm vi của giai đoạn này

| Trong phạm vi (làm ngay) | Ngoài phạm vi (hậu kỳ, giai đoạn sau) |
|---|---|
| Viết kịch bản: giảm kể gián tiếp, tăng thoại trực tiếp và diễn xuất | Chọn một giọng hay nhiều giọng (Cấu hình 1 / Cấu hình 2) |
| Chỉ đạo cảnh: ai nói với ai, hành động, cảm xúc, phản ứng, nhịp ngắt, liên tục | Giữ hay bỏ âm thanh gốc của clip |
| Góc máy có động cơ, phục vụ diễn biến | Đồng bộ khẩu hình (lip-sync) |

**Ràng buộc tương thích hiện tại:** hậu kỳ đang đọc trường `voiceover` của từng cảnh, animator đọc `image_prompt` + `motion`. Vì vậy các trường mới (mục 7) là **bổ sung**, không xoá trường cũ, và `voiceover`/`motion`/`image_prompt` phải được viết lại theo tinh thần diễn xuất (mục 7.3).

---

## 1. Nguyên tắc cốt lõi: **Diễn, đừng kể**

1. **Quy tắc chuyển đổi:** nếu một thông tin có thể thể hiện bằng *hành động, đối thoại hoặc phản ứng* của nhân vật thì **không được kể bằng lời dẫn**.
2. Lời dẫn (narration) chỉ dùng cho 4 việc:
   - mở móc câu (hook) đầu phim;
   - chuyển thời gian / không gian ("Ba đêm sau…");
   - điều không thể quay được (ký ức xa, lời đồn cả làng);
   - dư âm kết phim.
3. Trong một cảnh có diễn, lời dẫn **tối đa 1 câu ngắn** (≤ 15 chữ), đặt trước hoặc sau thoại, không chen giữa các lượt thoại.
4. Khán giả phải **hiểu chuyện bằng mắt**: nếu tắt tiếng mà vẫn đoán được ai đang áp đảo ai, ai đang giấu điều gì — cảnh đạt.

### 1.1 Ví dụ Kể → Diễn (lấy từ lỗi thật của tập `ep51`)

| ❌ Kể (bị loại) | ✅ Diễn (đạt) |
|---|---|
| "A Sáng là cháu nội nhà họ Thẩm, hai mươi sáu tuổi, áo dài xanh, **cậu nói cậu nghe tiếng đồn** về nhà họ Thẩm, trong nhà có ba điều cấm khi canh linh cữu." | A Sáng dừng ở bậc cửa, giũ nước mưa khỏi vạt áo. Bà Cả chặn ngang, không nhìn cậu: **"Ba đêm. Không ai được bước ra khỏi gian này."** A Sáng liếc về phía quan tài: **"Kể cả con?"** Bà quay lưng đi, không trả lời. |
| "Ông Đạo Sĩ là đạo sĩ bảy mươi tuổi, áo vải nâu sẫm, **ông nói** canh linh cữu có ba điều cấm, thứ nhất…, thứ hai…, thứ ba…" | Đạo sĩ gõ cán quạt lên nắp quan tài ba tiếng. **"Mèo đen. Đèn dầu. Nắp áo quan."** A Sáng: **"Nghĩa là sao, thầy?"** Đạo sĩ ghé sát tai cậu: **"Nghĩa là đừng để thứ nào xảy ra."** Ngọn đèn chao nghiêng. |

**Vì sao bản phải đạt:** tuổi, trang phục, gương mặt đã có trong `character_bible` và trong ảnh — **không bao giờ đọc lại**. Ba điều cấm được trao qua một hành động (gõ quạt) và một xung đột nhỏ (cậu hỏi, thầy không giải thích hết) → tạo tò mò.

---

## 2. Thoại

### 2.1 Mỗi câu thoại phải có ý đồ
Mỗi lượt thoại là một **hành động bằng lời** nhằm vào người nghe. Người viết phải biết động từ ý đồ của câu đó:
> *hỏi dồn · chối · doạ · dụ · giấu · thử · cầu xin · thách · ra lệnh · thú nhận · đánh lạc hướng · an ủi giả*

Nếu một câu thoại không đổi được quan hệ, thông tin hay áp lực giữa hai người → **cắt**.

### 2.2 Ẩn ý (subtext)
Nhân vật **không nói thẳng** điều họ cảm thấy hoặc điều họ giấu. Cảm xúc lộ qua cách né, cách cắt ngang, cách đổi chủ đề, qua cơ thể.
- ❌ "Tôi đang rất sợ, tôi nghĩ trong quan tài có ma."
- ✅ "…Thầy có nghe tiếng gì không?" (tay cậu siết quai đèn đến trắng khớp)

### 2.3 Giọng riêng của từng nhân vật
Khai báo trong `character_bible[].speech_style` (mục 7.1) và **giữ đúng suốt 38 cảnh**.
- **Phim Ma Dân Gian:** xưng hô làng quê theo vai vế (con/cháu/bác/thầy/u/mày–tao), câu ngắn, khẩu ngữ, kiêng kỵ nói thẳng chữ "ma" ("cái thứ đó", "người dưới kia").
- **Kiếm Hiệp (chất Cổ Long):** tại hạ/các hạ/cô nương/lão phu; câu ngắn, đối đáp sắc, nghịch lý, nói ít hiểu nhiều; kẻ mạnh thường nói chậm và ít.
- Hai nhân vật khác nhau không được nói giống nhau. Bài thử: che tên người nói, vẫn đoán được ai nói.

### 2.4 Cấm tuyệt đối
| Lỗi | Ví dụ bị loại |
|---|---|
| **Thoại thuyết minh** (nói điều cả hai đều biết cho khán giả nghe) | "Như cậu biết đấy, nhà họ Thẩm có ba điều cấm…" |
| **Tự giới thiệu hồ sơ** | "Ta là Lý Hàn, ba mươi tuổi, kiếm khách áo trắng…" |
| **Đọc lại điều vừa thấy** | (đèn vừa tắt) "Đèn tắt rồi!" — chỉ chấp nhận nếu câu đó mang thêm ý đồ khác |
| **Gọi tên cảm xúc** | "Ta rất giận." / "Con buồn lắm." |
| **Chuyển lời dẫn thành thoại** | Nhân vật đọc nguyên đoạn bối cảnh dài như người dẫn chuyện |
| **Lời gián tiếp** trong `voiceover` | "cậu nói rằng…", "ông bảo là…", "bà kể…" |

### 2.5 Độ dài & nhịp
- Mỗi lượt thoại **≤ 20 chữ**, ưu tiên 4–12 chữ.
- Một cảnh đối thoại: **2–4 lượt**. Dùng ngắt lời (`—`), câu bỏ lửng (`…`), và **im lặng có chủ đích** (ghi ở `beat_pause`).
- Thông tin lộ dần **qua xung đột**: một người giấu, một người truy. Không bao giờ để một nhân vật giải thích trọn vẹn bí mật trong một lượt.

---

## 3. Cấu trúc cảnh (beat)

### 3.1 Mỗi cảnh = một nhịp có thay đổi
Ghi vào trường `beat` một câu: **trước cảnh → chuyện xảy ra → sau cảnh**, ví dụ:
> "A Sáng tưởng chỉ là canh đêm bình thường → đạo sĩ trao 3 điều cấm mà không giải thích → cậu bắt đầu nghi có điều bị giấu."

Nếu trạng thái trước và sau giống nhau → cảnh thừa, gộp hoặc cắt.

### 3.2 Móc nối giữa các cảnh
Mỗi cảnh kết bằng một **móc** dẫn sang cảnh sau: câu hỏi chưa đáp, một âm thanh, một cử chỉ, một đạo cụ. Cảnh sau phải **bắt đúng móc đó** (ghi ở `continuity.from_prev`).

### 3.3 Phân bổ 4 Hồi (38 cảnh, giữ nguyên chuẩn thời lượng 6–8 phút)
| Hồi | Cảnh | Nhiệm vụ kịch tính |
|---|---|---|
| 1 | 1–9 | Hook mạnh · thiết lập điều cấm/luật chơi · mỗi nhân vật chính lộ **mong muốn** và **một điều giấu** · sự cố khởi phát |
| 2 | 10–19 | Điều tra / leo thang · đồng minh nghi ngờ nhau · **lật kèo 1** ở cuối hồi |
| 3 | 20–29 | Đối đầu trực diện · cái giá phải trả · **lật kèo 2** |
| 4 | 30–38 | Cao trào hành động · giải mã bằng hành động/đối chất (không bằng một đoạn kể) · dư âm |

### 3.4 Tỉ lệ bắt buộc toàn tập
- **≥ 60%** cảnh thuộc loại `doi_thoai` hoặc `hanh_dong` (có nhân vật diễn).
- **≤ 30%** cảnh `dan_truyen` (chỉ lời dẫn + hình minh hoạ).
- **Mỗi hồi ≥ 1 cảnh đối đầu trực diện** có ít nhất 2 nhân vật thoại qua lại.
- Giải mã bí mật ở Hồi 4 phải diễn ra **trong một cảnh đối chất**, không phải một đoạn kể tóm tắt.

---

## 4. Chỉ đạo diễn xuất trong từng cảnh

Với mỗi cảnh có diễn, đạo diễn phải trả lời đủ 6 câu:

| # | Câu hỏi | Trường |
|---|---|---|
| 1 | **Ai nói với ai?** | `dialogue[].speaker`, `dialogue[].to` |
| 2 | **Đứng ở đâu, hướng về đâu?** (vị trí, khoảng cách, ai cao/thấp hơn) | `blocking` |
| 3 | **Làm gì?** Động từ vật lý quan sát được | `action` |
| 4 | **Cảm xúc lộ ra thế nào trên cơ thể?** | `dialogue[].delivery`, `action` |
| 5 | **Người nghe phản ứng ra sao?** (bắt buộc cho cảnh thoại) | `reaction` |
| 6 | **Nhịp ngắt ở đâu?** Khoảnh khắc im lặng, ánh mắt, động tác dừng | `beat_pause` |

### 4.1 Cảm xúc phải "chụp được"
Không viết tính từ cảm xúc trơn. Viết thành hành vi:
- ❌ "A Sáng sợ hãi." → ✅ "A Sáng nuốt khan, lùi nửa bước, tay siết quai đèn dầu."
- ❌ "Lý Hàn tức giận." → ✅ "Lý Hàn đặt chén rượu xuống thật chậm; chén nứt một đường."

### 4.2 Phản ứng người nghe là một nửa của diễn xuất
Mọi cảnh thoại phải có `reaction`: người nghe làm gì *trong khi* hoặc *ngay sau khi* nghe. Khoảnh khắc lộ thông tin quan trọng → ưu tiên quay **mặt người nghe** (reaction shot), không phải mặt người nói.

---

## 5. Góc máy phục vụ diễn biến

### 5.1 Mỗi shot phải ghi đủ
`shot = { size, angle, subject, purpose, move }`
- **size:** establishing / wide / medium / two-shot / OTS (qua vai) / close-up / ECU (cận cực) / insert (vật) / POV.
- **angle:** eye-level / low (nhìn lên — áp đảo) / high (nhìn xuống — yếu thế) / dutch nhẹ (bất an) / top-down.
- **subject:** ai/cái gì là trọng tâm khung hình.
- **purpose:** vì sao chọn góc này cho diễn biến này (một câu).
- **move:** chuyển động **có động cơ** hoặc `static`. Động cơ hợp lệ: đi theo nhân vật đang di chuyển, lùi ra để lộ thứ khán giả chưa thấy, tiến vào khi nhân vật nhận ra điều gì, rack focus chuyển từ người nói sang người nghe.

### 5.2 Quy tắc chọn góc
- Đối thoại căng: **OTS / shot–reverse–shot**, giữ trục 180° (không đảo hướng nhìn giữa hai cảnh liên tiếp).
- Kẻ áp đảo: góc thấp; kẻ yếu thế/bị dồn: góc cao.
- Manh mối, vật chứng: **insert / ECU**.
- Khoảnh khắc lộ bí mật: **reaction close-up** của người nghe.
- Mở hồi / đổi không gian: establishing ngắn rồi vào ngay người.

### 5.3 Cấm ghi chung chung
Các cụm sau **không được đứng một mình** trong `motion` hay `shot.move`:
> "zoom chậm", "slow zoom", "slow push-in", "máy quay tiến vào", "camera moves forward", "slow pan", "cinematic shot", "slow crane shot", "slow tracking shot"

Chỉ chấp nhận khi đi kèm **chủ thể + động cơ**, ví dụ: *"slow push-in on A Sáng's face as he realises the lamp flame bends toward the coffin"*.

### 5.4 Ràng buộc khung dọc 9:16
- Two-shot dàn **tiền cảnh – hậu cảnh** (depth staging), không dàn trái–phải rộng.
- OTS: vai/gáy người nghe chiếm khoảng 1/3 dưới khung, mặt người nói ở 1/3 trên.
- Mặt nhân vật chính đặt trong 2/3 trên (chừa chỗ phụ đề phía dưới).

### 5.5 Ràng buộc clip AI Image-to-Video (mỗi cảnh = 1 ảnh → 1 clip vài giây)
- Mỗi cảnh chỉ **một khoảnh khắc diễn chính**, tối đa **2 hành động liên tiếp**.
- Không đổi góc máy bên trong một cảnh. Cần shot–reverse–shot → **tách thành 2 cảnh liên tiếp** (người nói / người nghe).
- Ảnh khung (`image_prompt`) phải bắt đúng **khoảnh khắc trước cao điểm** của hành động để clip có chỗ diễn tiếp.

---

## 6. Tính liên tục giữa các cảnh

Ghi `continuity = { from_prev, carry }`:
- `from_prev`: cảnh này bắt móc nào của cảnh trước.
- `carry`: những thứ phải giữ nguyên — vị trí đứng, hướng nhìn, đạo cụ đang cầm, vết thương, quần áo ướt/khô, thời tiết, nguồn sáng, thời điểm trong đêm.

Lỗi liên tục thường gặp cần tránh: đèn đã tắt lại sáng không lý do; nhân vật đang ở trong nhà bỗng đứng ngoài sân; tay phải cầm kiếm đổi sang tay trái; mưa tạnh rồi lại mưa trong cùng một đêm mà không có chuyển cảnh.

---

## 7. Lược đồ `episode.json` v2 (bổ sung, tương thích ngược)

### 7.1 Bổ sung cho `character_bible.characters[]`
| Trường | Ý nghĩa |
|---|---|
| `speech_style` | Cách nói: xưng hô, độ dài câu, khẩu ngữ, câu cửa miệng |
| `want` | Nhân vật muốn gì trong phim |
| `secret` | Điều nhân vật giấu (động cơ cho subtext) |

Các trường cũ (`id`, `name`, `age`, `gender`, `face`, `hair`, `costume`, `role`, `notes`, `voice`) **giữ nguyên**.

### 7.2 Bổ sung cho mỗi phần tử `scenes[]`
| Trường | Bắt buộc khi | Mô tả |
|---|---|---|
| `scene_type` | luôn | `doi_thoai` · `hanh_dong` · `dan_truyen` |
| `beat` | luôn | Trước → chuyện xảy ra → sau (một câu) |
| `characters_in_scene` | có nhân vật | Danh sách `id` nhân vật có mặt |
| `blocking` | `doi_thoai`, `hanh_dong` | Vị trí, khoảng cách, hướng nhìn |
| `action` | `doi_thoai`, `hanh_dong` | Hành động vật lý quan sát được |
| `dialogue` | `doi_thoai` | `[{speaker, to, line, intent, delivery}]` — `speaker`/`to` là `id` trong bible |
| `reaction` | `doi_thoai` | `{who, what}` phản ứng của người nghe |
| `beat_pause` | khuyến nghị | Khoảnh khắc ngắt/im lặng |
| `shot` | luôn | `{size, angle, subject, purpose, move}` |
| `continuity` | từ cảnh 2 | `{from_prev, carry}` |

Các trường cũ (`id`, `act`, `duration_s`, `clip`, `ghost`, `sfx`, `vo_at`, `voice`, `voiceover`, `image_prompt`, `motion`) **giữ nguyên tên**.

### 7.3 Cách viết 3 trường cũ đang được hệ thống tiêu thụ
- **`voiceover`** (hậu kỳ đọc thành tiếng): bản phát âm của cảnh. Cảnh `doi_thoai` viết **thoại trực tiếp trong ngoặc kép**, có tối đa 1 vế dẫn ngắn để người xem biết ai nói. Không chuyển sang lời gián tiếp. Không nhắc tuổi/trang phục. Giữ 30–45 chữ/cảnh để đủ thời lượng phim.
  > `Đạo sĩ gõ quạt lên nắp quan tài. "Mèo đen. Đèn dầu. Nắp áo quan." A Sáng nuốt khan: "Nghĩa là sao, thầy?" "Nghĩa là đừng để thứ nào xảy ra."`
- **`image_prompt`** (họa sĩ vẽ khung): khoảnh khắc chính của beat, **mô tả đủ các nhân vật có mặt, hướng nhìn, cử chỉ, cỡ cảnh và góc khớp `shot`**, dàn dựng chiều sâu cho khung dọc. Giữ nguyên tiền tố phong cách, khoá nhân vật và các cấm kỵ an toàn hiện có.
- **`motion`** (animator tạo clip): tiếng Anh, **diễn xuất trước, máy quay sau**:
  `"<nhân vật> <hành động vật lý>, <phản ứng người nghe>, <chuyển động môi trường>; camera: <chuyển động có động cơ hoặc static>"`
  > `"The old Daoist taps his fan on the coffin lid three times and leans toward A Sang; A Sang swallows and grips the oil lamp tighter, the flame bends sideways; camera: static OTS from behind A Sang's shoulder."`

### 7.4 Ví dụ một cảnh hoàn chỉnh
```json
{
  "id": 3, "act": 1, "duration_s": 12.0, "clip": "scene_03.mp4", "ghost": false,
  "scene_type": "doi_thoai",
  "beat": "A Sáng nghĩ chỉ là canh đêm thường → đạo sĩ trao 3 điều cấm mà không giải thích → cậu bắt đầu nghi có điều bị giấu.",
  "characters_in_scene": ["ong_dao_si", "a_sang"],
  "blocking": "Đạo sĩ đứng đầu quan tài, A Sáng đứng cuối quan tài; ngọn đèn dầu ở giữa hai người. Đạo sĩ ghé sát tai A Sáng ở lượt thoại cuối.",
  "action": "Đạo sĩ gõ cán quạt lên nắp quan tài ba tiếng, rồi bước vòng sang ghé tai A Sáng.",
  "dialogue": [
    {"speaker": "ong_dao_si", "to": "a_sang", "line": "Mèo đen. Đèn dầu. Nắp áo quan.", "intent": "ra lệnh", "delivery": "chậm, mỗi chữ một nhịp gõ quạt"},
    {"speaker": "a_sang", "to": "ong_dao_si", "line": "Nghĩa là sao, thầy?", "intent": "hỏi dồn", "delivery": "khẽ, mắt không rời quan tài"},
    {"speaker": "ong_dao_si", "to": "a_sang", "line": "Nghĩa là đừng để thứ nào xảy ra.", "intent": "giấu", "delivery": "thì thầm sát tai"}
  ],
  "reaction": {"who": "a_sang", "what": "Nuốt khan, siết quai đèn đến trắng khớp; ngọn lửa chao nghiêng về phía quan tài."},
  "beat_pause": "Sau tiếng gõ thứ ba: im lặng hai nhịp, chỉ còn tiếng mưa.",
  "shot": {"size": "OTS", "angle": "eye-level", "subject": "mặt đạo sĩ qua vai A Sáng", "purpose": "khán giả đứng ở vị trí A Sáng, nhận luật chơi cùng cậu", "move": "static"},
  "continuity": {"from_prev": "Bắt tiếng bước chân A Sáng dừng ở bậc cửa cảnh 2.", "carry": "A Sáng vẫn cầm đèn dầu tay phải, áo còn ướt mưa; nến trắng hai bên quan tài đang cháy."},
  "voiceover": "Đạo sĩ gõ quạt lên nắp quan tài. \"Mèo đen. Đèn dầu. Nắp áo quan.\" A Sáng nuốt khan: \"Nghĩa là sao, thầy?\" Ông ghé sát tai cậu: \"Nghĩa là đừng để thứ nào xảy ra.\"",
  "image_prompt": "Vertical 9:16 photorealistic 1960s rural Vietnamese folk horror cinema, 35mm film grain, …: over-the-shoulder shot from behind a 26-year-old young man holding an oil lamp, facing a 70-year-old Daoist in a dark brown robe who taps a folding fan on a coffin lid between them, white candles on both sides, the lamp flame leaning toward the coffin, depth staging, …",
  "motion": "The old Daoist taps his fan on the coffin lid three times and leans toward A Sang; A Sang swallows and grips the oil lamp tighter, the flame bends sideways; camera: static OTS from behind A Sang's shoulder.",
  "sfx": [{"at": 0, "gain_db": -23, "tag": "wood_knock"}], "vo_at": 0.12, "voice": "phonui"
}
```

---

## 8. Checklist tự kiểm trước khi nộp (Đạo diễn) / khi chấm (QA)

- [ ] ≥ 60% cảnh `doi_thoai`/`hanh_dong`, ≤ 30% `dan_truyen`, mỗi hồi có ≥ 1 cảnh đối đầu.
- [ ] Không có lời gián tiếp ("nói rằng", "bảo là", "kể rằng") trong `voiceover`.
- [ ] Không đọc lại tuổi / trang phục / gương mặt trong `voiceover` hoặc thoại.
- [ ] Mọi câu thoại ≤ 20 chữ và có `intent`; không thoại thuyết minh, không gọi tên cảm xúc.
- [ ] Mọi cảnh thoại có `reaction` của người nghe.
- [ ] Mọi `shot` đủ `size/angle/subject/purpose/move`; không cụm máy quay chung chung đứng một mình.
- [ ] `motion` bắt đầu bằng hành động của nhân vật, kết bằng `camera: …`.
- [ ] `continuity` có từ cảnh 2, các móc nối được bắt đúng.
- [ ] Đọc riêng các dòng thoại của từng nhân vật: giọng khác nhau, khớp `speech_style`.
- [ ] Bí mật được giải ở Hồi 4 bằng cảnh đối chất.

**Công cụ kiểm tự động:** `python studio/script_direction_lint.py <episode.json>` (trong repo `agentnet-corner-core`). Điểm `≥ 80` và `0` lỗi nghiêm trọng mới được coi là đạt chuẩn kịch bản v2. Công cụ chỉ bắt lỗi hình thức; QA vẫn phải đọc và chấm chất lượng diễn.

---

## 9. Lịch sử thay đổi
| Phiên bản | Ngày | Thay đổi |
|---|---|---|
| v2.0 | 2026-11-28 | Bản đầu tiên của chuẩn "Diễn, đừng kể": thoại trực tiếp, chỉ đạo cảnh 6 câu hỏi, góc máy có động cơ, liên tục, schema v2 tương thích ngược. |

> Muốn sửa chuẩn: sửa file này trong Git, tăng số phiên bản, ghi vào bảng lịch sử, rồi chạy `python studio/pipeline/publish_role_docs.py` để cập nhật bản trên Hub. Không sửa chuẩn bằng lời nhắn trong một phiên chat.
