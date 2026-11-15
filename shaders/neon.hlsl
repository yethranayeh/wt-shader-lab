// Neon glow: bright glyphs bleed in their own colour.
// Optional sub-pixel chromatic aberration. No scanlines, no curve, no tint.

Texture2D shaderTexture : register(t0);
SamplerState samplerState : register(s0);

cbuffer PixelShaderSettings : register(b0) {
  float  Time;
  float  Scale;
  float2 Resolution;
  float4 Background;
};

#define GLOW_STRENGTH    0.80   // opacity of the halo
#define GLOW_THRESHOLD   0.40   // peak value a pixel must exceed to emit
#define GLOW_GAIN        1.40   // compensates for how much the blur dilutes thin strokes
#define GLOW_STEP_PX     2.0    // spacing between blur taps, in physical pixels

#define ENABLE_CHROMATIC_ABERRATION 1
#define CA_PIXELS        0.75   // red/blue split; 0.5-1.0 is subtle, above 1.5 gets soft

struct PSInput {
  float4 pos : SV_POSITION;
  float2 uv : TEXCOORD0;
};

// Peak channel, not luma: saturated blues and purples have low luma and
// would never glow, which matters when colour carries meaning.
float peak(float3 c) {
  return max(max(c.r, c.g), c.b);
}

// Threshold before blurring, not after. A thin stroke loses most of its
// brightness to a wide blur, so gating the blurred result hides exactly
// the brightest text.
float3 emit(float3 c) {
  float p = peak(c);
  return c * (max(p - GLOW_THRESHOLD, 0.0) / max(p, 1e-4));
}

// Same tap weights as upstream crt.hlsl; they already sum to 1.
static const float glowWeights[9] = { 0.102, 0.092, 0.081, 0.071, 0.061, 0.051, 0.041, 0.031, 0.021 };

float4 sampleAberrated(float2 uv) {
  float4 c = shaderTexture.Sample(samplerState, uv);

  #if ENABLE_CHROMATIC_ABERRATION
  float dx = CA_PIXELS * Scale / Resolution.x;
  c.r = shaderTexture.Sample(samplerState, uv + float2(dx, 0)).r;
  c.b = shaderTexture.Sample(samplerState, uv - float2(dx, 0)).b;
  #endif

  return c;
}

float3 glowField(float2 uv) {
  float2 dx = float2(GLOW_STEP_PX * Scale / Resolution.x, 0);
  float2 dy = float2(0, GLOW_STEP_PX * Scale / Resolution.y);

  float3 h = emit(shaderTexture.Sample(samplerState, uv).rgb) * glowWeights[0];
  float3 v = h;

  for (int i = 1; i < 9; i++) {
    h += emit(shaderTexture.Sample(samplerState, uv + i * dx).rgb) * glowWeights[i];
    h += emit(shaderTexture.Sample(samplerState, uv - i * dx).rgb) * glowWeights[i];
    v += emit(shaderTexture.Sample(samplerState, uv + i * dy).rgb) * glowWeights[i];
    v += emit(shaderTexture.Sample(samplerState, uv - i * dy).rgb) * glowWeights[i];
  }

  return (h + v) * 0.5;
}

float4 main(PSInput pin) : SV_TARGET {
  float4 color = sampleAberrated(pin.uv);
  float3 glow = saturate(glowField(pin.uv) * GLOW_GAIN);

  // Screen blend: adds light without pushing the glyph itself toward white,
  // so amber stays amber instead of turning yellow.
  color.rgb = 1 - (1 - color.rgb) * (1 - glow * GLOW_STRENGTH);

  return saturate(color);
}
