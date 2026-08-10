import React from 'react';

/**
 * Custom Brand Logo Component
 * Renders the stylized 'A' emblem with leaf curve accent.
 */
export default function AppLogo({ className = "w-7 h-7", color = "currentColor" }) {
  return (
    <svg
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Outer Stylized 'A' Frame & Leaf Outline */}
      <path
        d="M32 82 L50 14 L68 42 M38 82 L50 28 L56 42"
        stroke={color}
        strokeWidth="6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* Curved Leaf Sweep & Crossbar */}
      <path
        d="M28 76 C42 66 52 64 62 48 C72 32 68 20 62 16 C56 26 50 38 42 54 C34 66 30 72 28 76 Z"
        stroke={color}
        strokeWidth="5"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      {/* Leaf Inner Vein */}
      <path
        d="M52 50 C58 38 64 26 62 18"
        stroke={color}
        strokeWidth="4"
        strokeLinecap="round"
      />
      {/* Right Foot Accent */}
      <path
        d="M60 62 C68 70 76 78 82 82 M62 72 C70 78 74 80 78 82"
        stroke={color}
        strokeWidth="5.5"
        strokeLinecap="round"
      />
    </svg>
  );
}
