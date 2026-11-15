// "Signal degraded" look for unfocused panes.
// Bursts on a 3s cycle; set ANIMATE 0 for a frozen pattern with zero redraw cost.

Texture2D shaderTexture : register(t0);
SamplerState samplerState : register(s0);

cbuffer PixelShaderSettings : register(b0) {
  float  Time;
  float  Scale;
  float2 Resolution;
  float4 Background;
};

#define ANIMATE          1      // 0 = no Time reference, pane never redraws
#define DIM              0.70   // unfocused panes recede hard
#define BANDS            40.0   // horizontal tear zones
#define BAND_CHANCE      0.90   // share of rows that stay clean
#define BAND_DISPLACE    0.008  // tear width as a fraction of pane width
#define GHOST_PX         3.0    // vertical double-image offset
#define GHOST_MIX        0.18
#define STUCK_LINE       0.12   // baseline brightness of frozen scan lines
#define CA_BURST_PX      5.0    // red/blue split during a burst, in pixels
#define BURST_EVERY      3.0    // seconds per glitch slot
#define BURST_LENGTH     0.36   // seconds a burst lasts
#define BURST_CHANCE     0.60   // share of slots that fire

struct PSInput {
  float4 pos : SV_POSITION;
  float2 uv : TEXCOORD0;
};

float hash(float n) {
  return frac(sin(n * 12.9898) * 43758.5453);
}

float4 main(PSInput pin) : SV_TARGET {
  float2 uv = pin.uv;

  #if ANIMATE
  float t = Time;
  #else
  float t = 0.0;
  #endif

  float slot = floor(t / BURST_EVERY);
  float local = frac(t / BURST_EVERY) * BURST_EVERY;
  float burst = step(BURST_CHANCE, hash(slot + 7.3)) * step(local, BURST_LENGTH);

  // The tear pattern reshuffles every slot, and stretches during a burst.
  float amp = BAND_DISPLACE * (1.0 + 2.0 * burst);
  float band = floor(uv.y * BANDS);
  if (hash(band + slot * 13.7) > BAND_CHANCE - 0.06 * burst) {
    uv.x += (hash(band + 11.0 + slot * 5.1) - 0.5) * amp;
  }

  // Vertical shake only while a burst is firing.
  uv.y += (hash(floor(t * 30.0)) - 0.5) * 0.003 * burst;

  float4 color;

  // Signal arriving on three channels at three different times.
  // Burst only, so the pane stays colour-accurate the rest of the time.
  if (burst > 0.0) {
    float2 ca = float2(CA_BURST_PX * burst * Scale / Resolution.x, 0);
    color.r = shaderTexture.Sample(samplerState, uv + ca).r;
    color.g = shaderTexture.Sample(samplerState, uv).g;
    color.b = shaderTexture.Sample(samplerState, uv - ca).b;
    color.a = 1.0;
  } else {
    color = shaderTexture.Sample(samplerState, uv);
  }

  // Faint double image: reads as the signal arriving twice.
  float dy = GHOST_PX * Scale / Resolution.y;
  float3 ghost = shaderTexture.Sample(samplerState, uv + float2(0, dy)).rgb;
  color.rgb = lerp(color.rgb, ghost, GHOST_MIX);

  // Stuck rows, brighter while a burst is firing.
  float row = floor(pin.uv.y * Resolution.y);
  color.rgb += step(0.9975, hash(row + 0.5)) * (STUCK_LINE + 0.25 * burst);

  // Slow rolling band; this is the "still alive but not well" motion.
  float rollY = frac(0.63 - t * 0.03);
  color.rgb += 0.05 * exp(-pow((pin.uv.y - rollY) / 0.008, 2.0));

  // Interference streaks, burst only.
  float streak = hash(floor(pin.uv.y * 200.0) + floor(t * 60.0));
  color.rgb += burst * step(0.97, streak) * 0.18;

  color.rgb *= DIM;

  return saturate(color);
}
