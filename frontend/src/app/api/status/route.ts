import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

// GET /api/status
export async function GET(request: NextRequest) {
  const url = `${BACKEND_URL}/system/status`;
  console.log('Fetching system status from:', url);
  
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend error:', {
        status: response.status,
        statusText: response.statusText,
        body: errorText,
      });
      throw new Error(`Failed to fetch system status: ${response.statusText}`);
    }

    const status = await response.json();
    console.log('Successfully fetched system status:', status);
    return NextResponse.json(status);
  } catch (error) {
    console.error('Error fetching system status:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to fetch system status' },
      { status: 500 }
    );
  }
} 