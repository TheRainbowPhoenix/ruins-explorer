// ---- GIPK PAK (little-endian) ----
// Layout:
//   [Header]
//   [asset blobs... palette + data for each entry, anywhere]
//   [Index entries array]  <-- header.index_offset
//
// Each Entry:
//   name[32], profile, reserved0,
//   color_count, width, height, stride, reserved1,
//   palette_len, data_len, palette_off, data_off
//
// Tip: data_len is typically stride * height for packed rows.

#pragma endian little

// Optional: known image profiles (adjust as needed)
enum ImageProfile : u8 {
    IMAGE_MONO         = 1,
    IMAGE_MONO_ALPHA   = 2,
    IMAGE_GRAY         = 3,
    IMAGE_GRAY_ALPHA   = 4,
    IMAGE_P2_RGB565    = 5, // example
    IMAGE_P4_RGB565    = 6  // example used in your snippets
};

struct Header {
    char magic[4];          // "GIPK"
    u16  version;           // 1
    u16  count;             // number of entries in index
    u32  index_offset;      // absolute file offset of first Entry
    u32  reserved;          // 0
};

// ---- Index entry describing one asset
struct Entry {
    char         name[32];     // zero-terminated ASCII
    ImageProfile profile;      // u8 (or plain u8 if you prefer)
    u8           reserved0;

    u16 color_count;
    u16 width;
    u16 height;
    u16 stride;                // bytes per row in packed format
    u16 reserved1;

    u32 palette_len;
    u32 data_len;
    u32 palette_off;           // absolute file offset to palette bytes
    u32 data_off;              // absolute file offset to pixel bytes

    // ---- Overlays (click to jump to data)
    u8 palette[palette_len] @ palette_off;
    u8 pixels [data_len]    @ data_off;

    // (Optional) quick derived check visible in the sidebar
    // NOTE: ImHex shows these as fields but they don't occupy file space.
    // Remove if you prefer a strictly "pure" struct.
    u32 expected_data_len = stride * height;
    bool data_len_mismatch = data_len != expected_data_len;
};

// ---- Index array lives at header.index_offset
Header header @ 0x00;

Entry entries[header.count] @ header.index_offset;