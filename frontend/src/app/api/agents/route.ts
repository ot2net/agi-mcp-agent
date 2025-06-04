import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// GET /api/agents
export async function GET() {
  try {
    const url = `${API_BASE_URL}/agents/`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // 添加超时控制
      signal: AbortSignal.timeout(10000)
    });

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status} ${response.statusText}`);
    }

    const agents = await response.json();
    
    return NextResponse.json(agents);
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    
    // 只在开发环境记录详细错误
    if (process.env.NODE_ENV === 'development') {
      console.error('Error fetching agents:', error);
    }
    
    return NextResponse.json(
      { error: 'Failed to fetch agents', details: errorMessage },
      { status: 500 }
    );
  }
}

// POST /api/agents
export async function POST(request: NextRequest) {
  try {
    const url = `${API_BASE_URL}/agents/`;
    const body = await request.json();

    // 基本的输入验证
    if (!body.name || typeof body.name !== 'string') {
      return NextResponse.json(
        { error: 'Agent name is required and must be a string' },
        { status: 400 }
      );
    }

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(15000) // 创建操作允许更长时间
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Backend API error: ${response.status} ${response.statusText}. ${errorText}`);
    }

    const agent = await response.json();
    
    return NextResponse.json(agent, { status: 201 });
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    
    if (process.env.NODE_ENV === 'development') {
      console.error('Error creating agent:', error);
    }
    
    return NextResponse.json(
      { error: 'Failed to create agent', details: errorMessage },
      { status: 500 }
    );
  }
} 