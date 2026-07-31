export interface ChatResponseData {
  response: string;
  session_id: string;
}

export class APIService {
  private baseURL: string;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.baseURL = baseURL;
  }

  async checkHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseURL}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(3000),
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  async chat(message: string, context?: Record<string, any>, sessionId: string = 'default'): Promise<ChatResponseData> {
    const response = await fetch(`${this.baseURL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        context,
      }),
    });

    if (!response.ok) {
      let errorMessage = `API error: ${response.status}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) errorMessage = errorData.detail;
      } catch {
        // use default error message
      }
      throw new Error(errorMessage);
    }

    return response.json();
  }

  async getLessons() {
    return [
      {
        id: 'd1-slide-hackathon',
        name: 'Bài 1: Nhập môn Học Sâu (Deep Learning)',
        description: 'Tổng quan Học sâu, Kiến trúc Mạng Nơ-ron & Hàm kích hoạt',
        file: 'd1-slide-hackathon.pdf'
      },
      {
        id: 'd2-slide-hackathon',
        name: 'Bài 2: Mạng Nơ-ron Nâng cao',
        description: 'Kỹ thuật Học sâu nâng cao, Tối ưu hóa & Ứng dụng thực tế',
        file: 'd2-slide-hackathon.pdf'
      }
    ];
  }
}

export const apiService = new APIService();