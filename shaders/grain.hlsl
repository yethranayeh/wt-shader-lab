// Film grain only. No colour conversion, no geometry, no resampling.

Texture2D shaderTexture : register(t0);
SamplerState samplerState : register(s0);

cbuffer PixelShaderSettings : register(b0) {
  float  Time;
  float  Scale;
  float2 Resolution;
  float4 Background;
};

#define GRAIN_INTENSITY 0.02

struct PSInput {
  float4 pos : SV_POSITION;
  float2 uv : TEXCOORD0;
};

// Same noise curve as upstream crt.hlsl: a roughly normal distribution
// instead of uniform noise, which is what makes it read as film.
#define a0  0.151015505647689
#define a1 -0.5303572634357367
#define a2  1.365020122861334
#define b0  0.132089632343748
#define b1 -0.7607324991323768

float permute(float x) {
  x *= (34 * x + 1);
  return 289 * frac(x * 1 / 289.0);
}

float rand(inout float state) {
  state = permute(state);
  return frac(state / 41.0);
}

float grain(float2 uv) {
  float3 m = float3(uv, Time % 5 / 5) + 1.0;
  float state = permute(permute(m.x) + m.y) + m.z;

  float p = 0.95 * rand(state) + 0.025;
  float q = p - 0.5;
  float r2 = q * q;

  return q * (a2 + (a1 * r2 + a0) / (r2 * r2 + b1 * r2 + b0));
}

float4 main(PSInput pin) : SV_TARGET {
  float4 color = shaderTexture.Sample(samplerState, pin.uv);
  color.rgb += GRAIN_INTENSITY * grain(pin.uv);
  return saturate(color);
}
