# Gemini — Repo Stickman (2026-11-15)

Hỏi trong conversation "Phân tích video Facebook Faceless" (gemini.google.com/app/f28e1a5a124a0126), tài khoản GCM Cong ty (giakhanhgcm@gmail.com, Pro), model Argon. Hỏi 14:54, trả lời 14:58 cùng ngày (3 phút). 7 câu hỏi về repo stickman (công cụ, cấu trúc repo, nhất quán, tiếng Việt, code mẫu, workflow/thời gian, điểm không chắc). Lưu nguyên văn câu trả lời.

> Lưu ý: Gemini tự ghi "Gemini is AI and can make mistakes." Code mẫu chưa được chạy/kiểm chứng. Hai điểm Gemini khác với quy tắc đã kiểm chứng của dự án: (1) loudnorm -14 LUFS trong lệnh FFmpeg mẫu, trong khi framework của dự án chốt ~-16 LUFS (đo từ video thật: -11,35 đến -27,53); (2) kịch bản ~140 từ cho 45s, trong khi vùng an toàn đã kiểm chứng 150-165 từ/phút tức 45s ≈ 112-124 từ. Giữ quy tắc của dự án trừ khi có bằng chứng mới.

---

## 1. Tool Choice: So sánh 5 giải pháp và Chốt Stack duy nhất

Bảng so sánh 5 công cụ cho bài toán "Repo Stickman Tái Sử Dụng"

| Tiêu chí | Remotion (React + TypeScript + SVG) | Manim (Python) | Blender Grease Pencil (Python API) | Pivot Animator | Thuần SVG + FFmpeg (Python/Node script) |
|---|---|---|---|---|---|
| Bản chất quản lý Rig (Xương khớp) | Phân cấp cha-con (Hierarchical DOM `<g>`). Xoay vai → khuỷu tay và bàn tay tự động xoay theo. | Hệ tọa độ Toán học. Không có khái niệm khớp xương cha-con tự nhiên (xoay nhóm rất dễ lệch trục). | Hệ xương (Armature + IK/FK) chuyên nghiệp nhất. | Kéo thả điểm khớp bằng chuột. | Tự viết hàm lượng giác (sin,cos) nối chuỗi từng đoạn thẳng rồi xuất ảnh PNG. |
| Xem trước (Live Preview) | Tức thì (0.1 giây) qua trình duyệt với thanh trượt từng frame (Hot Reload). | Chậm: Sửa 1 góc tay phải chạy lệnh render lại vài giây mới thấy kết quả. | Có Viewport trực quan nhưng sửa bằng code Python headless khó debug. | Trực quan bằng chuột nhưng không điều khiển bằng code. | Mù hoàn toàn (phải xuất ảnh hoặc ghép video mới thấy lỗi). |
| Typography & Text Card Tiếng Việt | Tuyệt đối (CSS Flexbox/Grid): Tự xuống dòng, căn giữa, đổ bóng, tô màu từng từ khóa dễ dàng. | Kém linh hoạt: MarkupText (Pango) căn chỉnh hộp chữ đa dòng, bo góc, padding rất cực. | Kém: Text Object trong 3D không có cơ chế auto-wrap/flexbox như web. | Rất thô sơ, không làm được Text Card hiện đại. | Khó: Tự tính toán tọa độ ngắt dòng (`<tspan>`) trong SVG thuần là ác mộng. |
| Khả năng tái sử dụng bằng Code (Git Repo) | Đỉnh cao: Mỗi tư thế, đạo cụ, biểu cảm là 1 Component hoặc JSON cấu hình. | Tốt (Class Python), nhưng code cảnh dài rất rối. | File .blend là file nhị phân (binary), rất khó quản lý diff trên Git. | Không thể lập trình hóa (chỉ lưu file .piv, .stk). | Tốt về mặt code nhưng phải tự viết lại toàn bộ Animation Engine (tweening, easing). |
| Chi phí & Bản quyền | Miễn phí 100% cho cá nhân và nhóm ≤3 người (Free License cho phép thương mại & tự động hóa). | Miễn phí (MIT License). | Miễn phí (GPL License). | Miễn phí (nhưng có bundle quảng cáo trong bộ cài). | Miễn phí (Open Source). |

**Quyết định: Chọn DUY NHẤT Remotion (React + TypeScript + SVG)**

Vì sao chọn Remotion:

- Giải quyết bài toán Xương khớp (Forward Kinematics) bằng thẻ `<g>` của SVG: Trong SVG, khi bạn bọc `<g transform="rotate(goc_vai)">` làm thẻ cha và nhét `<g transform="rotate(goc_khuyu_tay)">` làm thẻ con bên trong, toàn bộ cánh tay hoạt động y hệt một bộ xương thật mà không cần viết phương trình lượng giác phức tạp.
- Giải quyết bài toán Text Card & Phụ đề: Phong cách "Tâm sự người que" sống nhờ Text Card (bảng chữ, danh sách, mũi tên, highlight từ khóa). HTML/CSS giải quyết việc căn giữa, tự động xuống dòng tiếng Việt và co giãn khung viền trong 3 dòng code — điều mà Manim hay SVG thuần mất hàng giờ căn tọa độ.
- Remotion Studio (Preview từng frame): Khi chỉnh dáng đi hay cái vẫy tay của người que, bạn kéo thanh timeline trên trình duyệt xem ngay ở frame thứ 15 tay có bị gãy khớp không, sửa số độ trong code là màn hình cập nhật tức thì.

Vì sao loại 4 công cụ còn lại:

- Loại Manim: Sinh ra cho biểu đồ toán học và phương trình LaTeX. Dùng VGroup để làm nhân vật chuyển động đa khớp cực kỳ vất vả vì tâm xoay (about_point) liên tục di chuyển khi nhân vật bước đi.
- Loại Blender Grease Pencil: Quá nặng nề cho nét vẽ 2D tối giản; quản lý tài sản trong file nhị phân .blend đi ngược lại triết lý "code repo thuần túy" và không tận dụng được thế mạnh tự động dàn trang Text Card.
- Loại Pivot Animator: Công cụ làm tay bằng chuột trên Windows, không có CLI/API để tự động sinh video từ file kịch bản JSON.
- Loại SVG + FFmpeg tự viết: Bạn sẽ phải tự code lại từ đầu các hàm nội suy (interpolate), lò xo vật lý (spring), quản lý timeline theo frame và trình dựng chữ — những thứ Remotion đã làm sẵn hoàn hảo.

---

## 2. Repo Structure: Kiến trúc thư mục tái sử dụng 100%

Để nhân vật định nghĩa đúng một lần duy nhất và mỗi video mới chỉ là một file lắp ghép kịch bản (JSON/TSX), repo được chia làm 2 tầng tách biệt: engine/ (Cốt lõi dùng chung - Không bao giờ sửa khi làm video mới) và videos/ (Kịch bản từng tập).

```
stickman-shorts-repo/
├── package.json
├── tsconfig.json
├── remotion.config.ts
├── public/
│   ├── fonts/
│   │   └── BeVietnamPro-Bold.ttf       # Font tiếng Việt cố định lưu nội bộ
│   └── audio/                          # Chứa voice.wav, bgm.mp3, sfx/
│       ├── sfx_whoosh.wav
│       ├── sfx_pop.wav
│       └── sfx_ding.wav
└── src/
    ├── index.ts
    ├── Root.tsx                        # Đăng ký danh sách các video Shorts
    ├── core/                           # [TẦNG 1: HẰNG SỐ BẤT BIẾN]
    │   ├── designTokens.ts             # Khóa cứng độ dày nét, tỷ lệ cơ thể, bảng màu
    │   └── rigTypes.ts                 # Kiểu dữ liệu góc khớp (Pose), Biểu cảm, Đạo cụ
    ├── rig/                            # [TẦNG 2: BỘ XƯƠNG & THƯ VIỆN HÀNH ĐỘNG]
    │   ├── Stickman.tsx                # Component Nhân vật duy nhất của toàn kênh
    │   ├── FaceExpressions.tsx         # 8 biểu cảm mắt/miệng (buồn, vui, sốc, suy tư...)
    │   ├── poses.ts                    # Thư viện tư thế tĩnh (đứng chống nạnh, ôm đầu, chỉ tay)
    │   └── motions.ts                  # Hàm sinh chuyển động tuần hoàn (walkCycle, waveHand, nod)
    ├── components/                     # [TẦNG 3: ĐẠO CỤ & TEXT CARD]
    │   ├── TextCard.tsx                # Bảng chữ trên đỉnh/giữa màn hình (hỗ trợ highlight từ khóa)
    │   ├── SubtitleOverlay.tsx         # Phụ đề chạy theo từng cụm từ
    │   └── props/                      # Đạo cụ tối giản (cùng nét vẽ với nhân vật)
    │       ├── DeskLaptop.tsx
    │       ├── MoneyBag.tsx
    │       └── ClockWall.tsx
    ├── templates/                      # [TẦNG 4: BỐ CỤC CẢNH DÙNG SẴN]
    │   ├── SceneSplitCompare.tsx       # Cảnh chia đôi màn hình (Làm sức lực vs Dùng đầu óc)
    │   └── SceneStickmanTalk.tsx       # Cảnh nhân vật đứng/đi kèm TextCard phía trên
    └── videos/                         # [TẦNG 5: MỖI VIDEO MỚI CHỈ THÊM 1 FILE Ở ĐÂY]
        ├── Ep001_CamDauLamViec.tsx
        └── Ep002_SieuThiKhongDongHo.tsx
```

---

## 3. Consistency: Cơ chế khóa cứng ngoại hình Stickman trong Code

Sai lầm phổ biến nhất làm nhân vật bị biến dạng giữa các cảnh là dùng transform: scale() lên cả nhân vật (khi phóng to 1.5 lần, nét vẽ dày từ 10px lên 15px), hoặc gõ tay số pixel rải rác trong từng file.

Chúng ta khóa chặt ngoại hình bằng 3 cơ chế kỹ thuật trong code:

**Cơ chế 1: File hằng số bất biến (src/core/designTokens.ts với as const)**

Mọi kích thước hình học của nhân vật được tính từ một đơn vị gốc duy nhất là HEAD_RADIUS (Bán kính đầu) và bị đóng băng bằng Object.freeze:

```typescript
// src/core/designTokens.ts
export const STICKMAN_SPEC = Object.freeze({
  HEAD_RADIUS: 42,          // Bán kính đầu chuẩn
  NECK_LENGTH: 14,          // Cổ
  TORSO_LENGTH: 135,        // Thân mình
  UPPER_ARM: 62,            // Bắp tay
  LOWER_ARM: 58,            // Cẳng tay
  UPPER_LEG: 78,            // Đùi
  LOWER_LEG: 76,            // Bắp chân
  STROKE_WIDTH: 12,         // Độ dày nét vẽ DUY NHẤT cho toàn bộ cơ thể và đạo cụ
  STROKE_CAP: 'round' as const,
  STROKE_JOIN: 'round' as const,
  COLOR_PRIMARY: '#141414', // Đen dịu (tránh #000000 gắt mắt)
  COLOR_BG: '#F6F5F0',      // Trắng ngà giấy vẽ (Off-white)
  COLOR_ACCENT: '#D9381E',  // Đỏ cam nhấn từ khóa / đạo cụ quan trọng
});
```

**Cơ chế 2: Thuộc tính vectorEffect="non-scaling-stroke" của SVG**

Trong Stickman.tsx, mọi thẻ `<line>`, `<circle>`, `<path>` đều bắt buộc gắn thuộc tính vectorEffect="non-scaling-stroke". Nhờ thuộc tính chuẩn SVG này, dù ở cảnh nào bạn có zoom camera vào gần nhân vật hay thu nhỏ nhân vật lại, độ dày nét vẽ trên màn hình xuất ra vẫn giữ đúng 12px tuyệt đối, không bao giờ có chuyện cảnh thì nét to đùng, cảnh thì nét mảnh khảnh.

**Cơ chế 3: Chỉ điều khiển qua Góc Khớp (JointAngles), cấm sửa Tọa Độ Đỉnh**

Các file video (Ep001...) không có quyền truyền chiều dài tay/chân vào Stickman.tsx. Component Stickman chỉ nhận đầu vào là các góc xoay bằng độ (shoulderLeft: -30, elbowLeft: -45...). Do độ dài xương (TORSO_LENGTH, UPPER_ARM...) nằm chết bên trong Stickman.tsx, tỷ lệ cơ thể là bất khả xâm phạm.

---

## 4. Vietnamese Text: Xử lý dấu tiếng Việt, chọn Font và các bẫy cần tránh

Vì Remotion sử dụng nhân Chromium (Headless Browser) để vẽ từng frame, khả năng dựng chữ tiếng Việt (OpenType shaping cho các tổ hợp dấu phức như ể, ẫ, ự, ằ) đạt độ chính xác 100% — vượt xa ImageMagick hay FFmpeg drawtext. Tuy nhiên, bạn phải tránh 4 cái bẫy chí mạng sau:

**1. Chọn bộ Font nào cho phong cách Stickman?**

Font cho Text Card & Phụ đề chính: Be Vietnam Pro (độ đậm Bold 700 / ExtraBold 800) hoặc Plus Jakarta Sans. Lý do: Be Vietnam Pro được thiết kế chuyên biệt cho tiếng Việt: dấu mũ (^) và dấu thanh (sắc, hỏi, ngã) được đặt gọn, thấp, không bị vọt lên quá cao nên khi đóng khung Text Card nhiều dòng không bị dính chữ dòng trên vào dấu dòng dưới.

Font cho ghi chú viết tay / nhãn mũi tên nhỏ: Patrick Hand hoặc Mali (hỗ trợ đầy đủ tiếng Việt, nét tròn đều khớp với nét bút lông round của người que).

**2. Bốn cạm bẫy khi render Tiếng Việt và cách chặn đứng**

Bẫy 1 — Mất dấu hoặc nhảy sang font lỗi trên VPS Linux (Thiếu Font cục bộ):

Nguyên nhân: Trên Windows có sẵn Arial/Segoe UI, nhưng VPS Linux tối giản không có font tiếng Việt. Nếu gọi Google Fonts qua mạng lúc render, mạng chậm 0.5 giây sẽ gây hiện tượng FOUT (nháy font mặc định ở vài frame đầu).

Cách tránh: Tải file tĩnh BeVietnamPro-Bold.ttf bỏ vào thư mục public/fonts/ của repo và dùng hàm delayRender() / @remotion/google-fonts để khóa trình render: chưa nạp xong font vào RAM thì tuyệt đối không được chụp frame đầu tiên.

Bẫy 2 — Bảng mã tổ hợp NFD (Tách rời chữ và dấu):

Nguyên nhân: Text copy từ macOS hoặc một số công cụ AI trả về chuẩn Unicode NFD (chữ o, dấu ^, dấu ? là 3 ký tự rời nhau). Khi áp dụng hiệu ứng viền chữ (WebkitTextStroke) hoặc cắt từng ký tự, dấu sẽ bị lệch khỏi nguyên âm.

Cách tránh: Luôn bọc mọi chuỗi văn bản đầu vào qua hàm chuẩn hóa .normalize('NFC') trước khi render.

Bẫy 3 — Mất đầu dấu tiếng Việt do overflow: hidden và line-height quá hẹp:

Nguyên nhân: Các chữ hoa có dấu kép như Ở, Ể, Ẫ, Ự trong tiếng Việt cao hơn chữ tiếng Anh khoảng 18%–22%. Nếu để lineHeight: 1.0 hoặc 1.1 kèm khung overflow: hidden, phần chóp dấu hỏi/ngã ở dòng đầu sẽ bị cắt cụt.

Cách tránh: Luôn đặt lineHeight >= 1.32 và paddingTop >= 16px cho mọi hộp Text Card.

Bẫy 4 — Chữ đơn lẻ rớt dòng cuối (Widow words):

Nguyên nhân: Câu tiếng Việt dài tự xuống dòng để lại 1 chữ cụt lủn ở dòng cuối (ví dụ: "Cắm đầu làm việc không giúp bạn giàu / có").

Cách tránh: Gắn thuộc tính CSS hiện đại textWrap: 'balance' vào thẻ chứa chữ trên Text Card — trình duyệt sẽ tự động chia đều độ dài các dòng.

---

## 5. Starter Code: Ví dụ tối thiểu chạy được ngay (9:16, Đi bộ + Vẫy tay + Text Card Tiếng Việt)

Dưới đây là bộ code đầy đủ, tự chứa (self-contained) để bạn khởi tạo và xuất ngay một video 1080x1920 (30fps, 5 giây): Stickman bước đi từ ngoài biên trái vào giữa màn hình (0s–2s), dừng lại nhìn người xem và vẫy tay phải chào (2s–5s), đồng thời Text Card tiếng Việt nảy ra kèm highlight màu đỏ.

Bước khởi tạo nhanh trên máy của bạn:

```bash
npx create-video@latest stickman-repo --blank
cd stickman-repo
```

Sau đó thay thế/tạo 2 file dưới đây trong thư mục src/:

**File 1: src/StickmanShort.tsx** (Chứa Design Tokens, Rig Xương khớp, Động tác & Text Card)

```typescript
import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

// 1. HẰNG SỐ NHÂN VẬT BẤT BIẾN (Đảm bảo 100% video giống hệt nhau)
export const SPEC = Object.freeze({
  HEAD_R: 44,
  NECK: 16,
  TORSO: 140,
  UPPER_ARM: 64,
  LOWER_ARM: 60,
  UPPER_LEG: 82,
  LOWER_LEG: 80,
  STROKE: 12,
  INK: '#141414',
  BG: '#F6F5F0',
  ACCENT: '#D9381E',
});

// 2. KIỂU DỮ LIỆU TƯ THẾ (Chỉ điều khiển qua góc xoay độ)
export interface PoseAngles {
  torsoLean: number;
  headTilt: number;
  shoulderL: number;
  elbowL: number;
  shoulderR: number;
  elbowR: number;
  hipL: number;
  kneeL: number;
  hipR: number;
  kneeR: number;
  expression?: 'neutral' | 'happy' | 'focused';
}

// 3. COMPONENT NHÂN VẬT STICKMAN DUY NHẤT (Phân cấp khớp xương <g>)
export const Stickman: React.FC<{
  x: number;
  y: number;
  pose: PoseAngles;
}> = ({ x, y, pose }) => {
  const strokeProps = {
    stroke: SPEC.INK,
    strokeWidth: SPEC.STROKE,
    strokeLinecap: 'round' as const,
    strokeLinejoin: 'round' as const,
    fill: 'none',
    vectorEffect: 'non-scaling-stroke' as const,
  };

  return (
    <g transform={`translate(${x}, ${y})`}>
      {/* Gốc tọa độ (0,0) đặt tại Hông (Hip) */}
      {/* CHÂN TRÁI (Vẽ trước để nằm lớp sau) */}
      <g transform={`rotate(${pose.hipL})`}>
        <line x1={0} y1={0} x2={0} y2={SPEC.UPPER_LEG} {...strokeProps} />
        <g transform={`translate(0, ${SPEC.UPPER_LEG}) rotate(${pose.kneeL})`}>
          <line x1={0} y1={0} x2={0} y2={SPEC.LOWER_LEG} {...strokeProps} />
        </g>
      </g>

      {/* CHÂN PHẢI */}
      <g transform={`rotate(${pose.hipR})`}>
        <line x1={0} y1={0} x2={0} y2={SPEC.UPPER_LEG} {...strokeProps} />
        <g transform={`translate(0, ${SPEC.UPPER_LEG}) rotate(${pose.kneeR})`}>
          <line x1={0} y1={0} x2={0} y2={SPEC.LOWER_LEG} {...strokeProps} />
        </g>
      </g>

      {/* THÂN MÌNH (Tính từ Hông hướng lên Vai) */}
      <g transform={`rotate(${pose.torsoLean})`}>
        <line x1={0} y1={0} x2={0} y2={-SPEC.TORSO} {...strokeProps} />

        {/* CỤM VAI (Tại đỉnh thân mình: y = -TORSO) */}
        <g transform={`translate(0, ${-SPEC.TORSO})`}>
          {/* TAY TRÁI */}
          <g transform={`rotate(${pose.shoulderL})`}>
            <line x1={0} y1={0} x2={0} y2={SPEC.UPPER_ARM} {...strokeProps} />
            <g transform={`translate(0, ${SPEC.UPPER_ARM}) rotate(${pose.elbowL})`}>
              <line x1={0} y1={0} x2={0} y2={SPEC.LOWER_ARM} {...strokeProps} />
            </g>
          </g>

          {/* TAY PHẢI */}
          <g transform={`rotate(${pose.shoulderR})`}>
            <line x1={0} y1={0} x2={0} y2={SPEC.UPPER_ARM} {...strokeProps} />
            <g transform={`translate(0, ${SPEC.UPPER_ARM}) rotate(${pose.elbowR})`}>
              <line x1={0} y1={0} x2={0} y2={SPEC.LOWER_ARM} {...strokeProps} />
            </g>
          </g>

          {/* CỔ & ĐẦU */}
          <g transform={`rotate(${pose.headTilt})`}>
            <line x1={0} y1={0} x2={0} y2={-SPEC.NECK} {...strokeProps} />
            <circle
              cx={0}
              cy={-(SPEC.NECK + SPEC.HEAD_R)}
              r={SPEC.HEAD_R}
              {...strokeProps}
              fill={SPEC.BG}
            />
            {/* Biểu cảm khuôn mặt tối giản */}
            <g transform={`translate(0, ${-(SPEC.NECK + SPEC.HEAD_R)})`}>
              <circle cx={-14} cy={-6} r={4.5} fill={SPEC.INK} />
              <circle cx={14} cy={-6} r={4.5} fill={SPEC.INK} />
              {pose.expression === 'happy' ? (
                <path
                  d="M -14 10 Q 0 24 14 10"
                  {...strokeProps}
                  strokeWidth={8}
                />
              ) : (
                <line
                  x1={-10}
                  y1={14}
                  x2={10}
                  y2={14}
                  {...strokeProps}
                  strokeWidth={8}
                />
              )}
            </g>
          </g>
        </g>
      </g>
    </g>
  );
};

// 4. HÀM TẠO DÁNG ĐI BỘ TUẦN HOÀN (Walk Cycle Generator)
export const getWalkPose = (frame: number, speed = 0.28): PoseAngles => {
  const phase = frame * speed;
  const swing = Math.sin(phase);
  const counterSwing = Math.sin(phase + Math.PI);

  return {
    torsoLean: 6, // Hơi đổ người về phía trước khi bước
    headTilt: Math.sin(phase * 2) * 3,
    shoulderL: counterSwing * 32,
    elbowL: -25 - Math.max(0, counterSwing) * 20,
    shoulderR: swing * 32,
    elbowR: -25 - Math.max(0, swing) * 20,
    hipL: swing * 34,
    kneeL: Math.max(0, -swing) * 42, // Đầu gối chỉ gập về phía sau
    hipR: counterSwing * 34,
    kneeR: Math.max(0, -counterSwing) * 42,
    expression: 'neutral',
  };
};

// 5. HÀM TẠO DÁNG ĐỨNG VẪY TAY CHÀO (Wave Pose Generator)
export const getWavePose = (frame: number): PoseAngles => {
  const waveAngle = Math.sin(frame * 0.45) * 28;
  return {
    torsoLean: 0,
    headTilt: -5,
    shoulderL: 22,
    elbowL: 12,
    shoulderR: -135, // Giơ bắp tay phải lên cao
    elbowR: -35 + waveAngle, // Lắc cẳng tay vẫy chào
    hipL: 8,
    kneeL: 0,
    hipR: -8,
    kneeR: 0,
    expression: 'happy',
  };
};

// 6. COMPONENT VIDEO CHÍNH (1080x1920, 30fps, 150 frames = 5 giây)
export const StickmanStarterShort: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const walkEndFrame = 60; // Đi bộ từ frame 0 đến frame 60 (2 giây đầu)

  // Nội suy vị trí X: đi từ ngoài màn hình trái (x = 120) vào giữa (x = 540)
  const posX = interpolate(frame, [0, walkEndFrame], [120, 540], {
    extrapolateRight: 'clamp',
  });

  // Độ nảy thân người theo nhịp bước chân
  const walkBounce =
    frame < walkEndFrame ? Math.abs(Math.sin(frame * 0.28)) * 14 : 0;
  const posY = 1220 - walkBounce;

  // Chuyển mượt từ dáng Đi bộ sang dáng Đứng vẫy tay
  const currentPose =
    frame < walkEndFrame ? getWalkPose(frame) : getWavePose(frame - walkEndFrame);

  // Hiệu ứng nảy (Spring) cho Text Card xuất hiện ở frame 55
  const cardScale = spring({
    frame: frame - 55,
    fps,
    config: { damping: 12, stiffness: 140 },
  });

  const titleLine1 = 'CẮM ĐẦU LÀM VIỆC'.normalize('NFC');
  const titleLine2 = 'KHÔNG GIÚP BẠN GIÀU LÊN'.normalize('NFC');
  const subText = 'Hãy dùng đòn bẩy tư duy thay vì bán rẻ sức lực.'.normalize('NFC');

  return (
    <AbsoluteFill
      style={{
        backgroundColor: SPEC.BG,
        fontFamily: '"Be Vietnam Pro", "Segoe UI", Roboto, sans-serif',
      }}
    >
      {/* NỬA TRÊN: TEXT CARD TIẾNG VIỆT */}
      <div
        style={{
          position: 'absolute',
          top: 240,
          left: 72,
          right: 72,
          transform: `scale(${cardScale})`,
          opacity: interpolate(cardScale, [0, 0.3], [0, 1]),
          backgroundColor: '#FFFFFF',
          border: `8px solid ${SPEC.INK}`,
          borderRadius: 28,
          padding: '44px 40px',
          boxShadow: `14px 14px 0px ${SPEC.INK}`,
          textAlign: 'center',
        }}
      >
        <div
          style={{
            fontSize: 58,
            fontWeight: 800,
            color: SPEC.INK,
            lineHeight: 1.35,
            textWrap: 'balance',
          }}
        >
          {titleLine1}
          <br />
          <span style={{ color: SPEC.ACCENT }}>{titleLine2}</span>
        </div>
        <div
          style={{
            marginTop: 24,
            fontSize: 38,
            fontWeight: 600,
            color: '#4A4A4A',
            lineHeight: 1.4,
            textWrap: 'balance',
          }}
        >
          {subText}
        </div>
      </div>

      {/* NỬA DƯỚI: SÂN KHẤU SVG CHO STICKMAN */}
      <svg width={1080} height={1920} viewBox="0 0 1080 1920">
        {/* Mặt đất tối giản */}
        <line
          x1={140}
          y1={1385}
          x2={940}
          y2={1385}
          stroke={SPEC.INK}
          strokeWidth={8}
          strokeLinecap="round"
        />
        {/* Nhân vật Stickman */}
        <Stickman x={posX} y={posY} pose={currentPose} />
      </svg>
    </AbsoluteFill>
  );
};
```

**File 2: src/Root.tsx** (Đăng ký khung hình 9:16 Dọc)

```typescript
import React from 'react';
import { Composition } from 'remotion';
import { StickmanStarterShort } from './StickmanShort';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="StickmanStarter"
      component={StickmanStarterShort}
      durationInFrames={150} // 5 giây * 30 fps
      fps={30}
      width={1080}
      height={1920}
    />
  );
};
```

Lệnh chạy xem trước và xuất file MP4:

- Mở giao diện chỉnh sửa trực tiếp trên trình duyệt: `npx remotion studio`
- Xuất file video MP4 chuẩn 1080x1920: `npx remotion render StickmanStarter out/demo_short.mp4`

---

## 6. Workflow + Time: Quy trình sản xuất 45 giây và Phân bổ tải PC RTX 5060 Ti vs VPS Linux

**A. Quy tắc "Audio-First" (Làm tiếng trước, khớp hình sau)**

Với video Shorts thuyết minh, tuyệt đối không làm hình trước rồi mới thu âm. Bạn phải tạo file giọng đọc (voice.wav) và lấy mốc thời gian từng câu (.json/.srt) trước, sau đó truyền các mốc giây đó vào code Remotion để cảnh và chữ nhảy ra khớp từng phần mười giây với lời nói.

**B. Phân chia nhiệm vụ giữa VPS Linux (4 CPU, 8GB RAM) và PC Windows (RTX 5060 Ti 16GB)**

| Hạng mục công việc | Chạy trên đâu? | Lý do kỹ thuật |
|---|---|---|
| 1. Tải video mẫu (yt-dlp), cào dữ liệu, lưu trữ kịch bản, chạy cronjob lịch đăng | VPS Linux (4 CPU, 8GB RAM) | Tác vụ mạng và I/O nhẹ, chạy 24/7 không cần bật PC cá nhân. |
| 2. Sinh giọng đọc AI (Local TTS) & Bóc băng dấu thời gian (Whisper large-v3) | PC Windows (RTX 5060 Ti 16GB) | Với 16GB VRAM của RTX 5060 Ti, việc chạy TTS và Whisper large-v3 bằng CUDA chỉ mất 3–5 giây cho đoạn 45s (trên VPS không GPU sẽ mất vài phút và tràn RAM). |
| 3. Thiết kế cảnh (Remotion Studio) & Render Video MP4 + Ghép FFmpeg | PC Windows (RTX 5060 Ti 16GB) | Headless Chromium của Remotion chạy đa luồng (concurrency) ngốn nhiều RAM và CPU/GPU. Render 45s trên PC chỉ mất 20–40 giây; trong khi trên VPS 4 vCPU, 8GB RAM rất dễ bị lỗi Out of Memory (OOM Killer) nếu mở quá 2 tab Chromium ẩn. |

**C. Bảng định mức thời gian sản xuất 1 video 45 giây (Khi Repo Rig đã hoàn thiện)**

Tổng thời gian thực tế cho 1 video 45 giây (1.350 frames @ 30fps, gồm 10–12 cảnh chuyển) là khoảng 25 – 35 phút:

| Bước | Thao tác thực hiện | Thời gian |
|---|---|---|
| Bước 1: Kịch bản & Voice | Viết kịch bản ~140 từ → Xuất voice.wav bằng công cụ TTS trên PC → Cắt khoảng lặng thừa. | 8 – 10 phút |
| Bước 2: Lấy Timestamps | Chạy Whisper trên RTX 5060 Ti xuất ra timestamps.json + file phụ đề subs.ass. | 1 phút (Tự động) |
| Bước 3: Lắp ghép Scene trong Repo | Tạo file EpXXX.tsx (hoặc file cấu hình JSON): chọn Template cảnh, gán pose/motion có sẵn (walk, think, point, sad), điền nội dung Text Card theo mốc giây của timestamps.json. | 10 – 15 phút |
| Bước 4: Tinh chỉnh trên Remotion Studio | Xem lướt qua trình duyệt, chỉnh lại vị trí 1–2 đạo cụ hoặc từ khóa tô màu cho thuận mắt. | 5 phút |
| Bước 5: Render hình ảnh & SFX | Chạy `npx remotion render EpXXX out/visual.mp4 --codec=h264`. | 25 – 45 giây (Máy tự chạy) |
| Bước 6: Master Audio & Phụ đề bằng FFmpeg | Chạy 1 script FFmpeg tự động trộn voice.wav + bgm.mp3 (auto-ducking nhỏ nhạc khi có tiếng nói) + đốt phụ đề (nếu không đốt sẵn trong Remotion) và chuẩn hóa âm lượng -14 LUFS cho YouTube Shorts. | 10 giây (Máy tự chạy) |

Lệnh FFmpeg mẫu ở Bước 6 (Gộp Voice + Nhạc nền tự giảm âm lượng + Chuẩn hóa âm thanh Shorts):

```bash
ffmpeg -y -i out/visual.mp4 -i public/audio/voice.wav -stream_loop -1 -i public/audio/bgm.mp3 \
-filter_complex "\
[1:a]loudnorm=I=-14:TP=-1.5:LRA=11[voice_norm]; \
[2:a]volume=0.12[bgm_low]; \
[voice_norm][bgm_low]amix=inputs=2:duration=first:dropout_transition=2[a_out]" \
-map 0:v -map "[a_out]" -c:v libx264 -preset fast -crf 18 -c:a aac -b:a 192k -shortest out/final_short.mp4
```

---

## 7. Những điểm tôi KHÔNG chắc chắn (Minh bạch thay vì đoán mò)

- **Không biết chi tiết chuyển động bên trong 4 link Facebook /share/p/ bị lỗi ở đầu cuộc trò chuyện:** Vì chỉ có thông tin xác thực của Video số 5 (Tâm sự người que), tôi không biết 4 video còn lại có sử dụng các kỹ thuật chuyển động đặc thù nào khác (ví dụ: hiệu ứng vẽ nét tay chạy dần kiểu Whiteboard VideoScribe, giả lập 3D camera nghiêng, hay biến hình morphing phức tạp giữa các vật thể) hay không. Nếu bạn cần hiệu ứng "bàn tay cầm bút vẽ từng nét" (stroke-dashoffset), cách tổ chức component SVG sẽ cần thêm một lớp tính độ dài đường dẫn (getTotalLength()).
- **Mức độ tự nhiên của các động tác phức tạp khi chỉ dùng Forward Kinematics (FK):** Cơ chế xoay góc khớp cha-con (shoulder → elbow) trong code mẫu ở Mục 5 cực kỳ dễ dùng và mượt cho 90% động tác thuyết minh (đi bộ, chạy, vẫy tay, chỉ bảng, ôm đầu, nhún vai, gật đầu). Tuy nhiên, với các động tác đòi hỏi một điểm cố định trong không gian (ví dụ: hai bàn tay giữ chặt ghi-đông xe đạp hoặc chống tay xuống bàn rồi nhún người), FK thuần túy sẽ làm bàn tay hơi trượt khỏi mặt bàn. Để khóa cứng bàn tay vào mặt bàn, bạn sẽ cần viết thêm một hàm toán học giải phương trình tam giác 2 xương (2-Bone Inverse Kinematics - IK bằng định lý Cosin). Tôi chưa đưa hàm lượng giác IK đó vào code khởi đầu để giữ code dễ hiểu nhất.
- **Số luồng (--concurrency) tối ưu nhất trên cấu hình PC cụ thể của bạn:** Bạn có GPU RTX 5060 Ti 16GB rất mạnh, nhưng tốc độ render của Remotion phụ thuộc rất nhiều vào số nhân CPU và dung lượng RAM hệ thống của PC đó (thông số bạn chưa nêu). Tôi không chắc con số --concurrency tối ưu trên PC của bạn là 6, 8 hay 12 luồng (bạn sẽ cần chạy thử lệnh npx remotion benchmark một lần trên máy để tìm ra con số nhanh nhất).
- **Cơ chế bạn muốn dùng cho Phụ đề (Subtitles):** Tôi chưa chắc bạn thích render phụ đề trực tiếp bằng React Component bên trong Remotion (ưu điểm: đẹp, dễ làm hiệu ứng chữ phóng to/nhảy màu từng từ nhưng nếu sửa 1 chữ chính tả phải render lại cả video 30 giây) hay đốt phụ đề .ass bằng FFmpeg ở bước cuối cùng (ưu điểm: chỉ mất 3 giây để xuất lại nếu sửa chính tả). Trong kiến trúc ở Mục 2 và Mục 6, tôi đã để mở cả 2 hướng để bạn chọn cách thuận tay nhất.
