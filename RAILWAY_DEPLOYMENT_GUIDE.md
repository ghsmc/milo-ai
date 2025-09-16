# Railway Deployment Guide - Milo Streaming Chat

## 🚀 Quick Deployment Steps

### 1. **Commit Your Changes**
```bash
git add .
git commit -m "Add streaming chat functionality with 6-step career discovery"
git push origin main
```

### 2. **Railway Auto-Deploy**
Railway will automatically detect your changes and redeploy. The deployment will:
- Use your existing `railway.json` configuration
- Start with `uvicorn app:app --host 0.0.0.0 --port $PORT`
- Include all new streaming chat endpoints

### 3. **Verify Deployment**
Once deployed, check these endpoints:

- **Health Check**: `https://your-railway-url.railway.app/health`
- **API Docs**: `https://your-railway-url.railway.app/docs`
- **Streaming Chat**: `https://your-railway-url.railway.app/chat/stream`

## 📋 What's Been Updated

### **New Endpoints Added to app.py**
- `POST /chat/stream` - Streaming chat responses
- `GET /chat/history/{session_id}` - Conversation history
- `GET /chat/session/{session_id}` - Session information
- `DELETE /chat/session/{session_id}` - Clear session
- `GET /chat/sessions` - List all sessions

### **Enhanced Features**
- ✅ **Latest OpenAI Model**: Now uses GPT-4o
- ✅ **Real-time Streaming**: Server-Sent Events (SSE)
- ✅ **Conversation Context**: Maintains chat history
- ✅ **6-Step Career Discovery**: Structured conversation flow
- ✅ **Session Management**: Multiple concurrent conversations

## 🔧 Configuration

### **Environment Variables Required**
Make sure these are set in your Railway project:

```bash
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=your_postgresql_url_here  # Optional
```

### **Railway Configuration**
Your `railway.json` is already configured correctly:
```json
{
  "deploy": {
    "startCommand": "uvicorn app:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health"
  }
}
```

## 🧪 Testing Your Deployment

### **1. Health Check**
```bash
curl https://your-railway-url.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "milo-ai-backend",
  "milo_available": true,
  "streaming_chat_available": true,
  "features": ["career_analysis", "streaming_chat", "session_management"]
}
```

### **2. Test Streaming Chat**
```bash
curl -X POST https://your-railway-url.railway.app/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "I love data science and global issues", "session_id": "test"}'
```

### **3. Test Session Management**
```bash
# Get session info
curl https://your-railway-url.railway.app/chat/session/test

# Get chat history
curl https://your-railway-url.railway.app/chat/history/test

# List all sessions
curl https://your-railway-url.railway.app/chat/sessions
```

## 🌐 Frontend Integration

### **Update Your Frontend**
To use the new streaming chat, update your frontend to call:

```javascript
// Streaming chat endpoint
const response = await fetch('https://your-railway-url.railway.app/chat/stream', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: userMessage,
    session_id: sessionId
  })
});

// Handle streaming response
const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      if (data.content) {
        // Display streaming content
        displayMessage(data.content);
      }
    }
  }
}
```

## 📊 Monitoring

### **Railway Dashboard**
- Monitor deployment status
- Check logs for any errors
- View resource usage

### **Health Endpoint**
The `/health` endpoint now includes:
- Streaming chat availability
- Feature list
- Service status

## 🔄 Rollback Plan

If you need to rollback:

```bash
# Rollback to previous commit
git revert HEAD
git push origin main
```

Or use Railway's rollback feature in the dashboard.

## 🐛 Troubleshooting

### **Common Issues**

1. **OpenAI API Key Missing**
   - Check Railway environment variables
   - Verify `OPENAI_API_KEY` is set

2. **Streaming Not Working**
   - Check browser console for CORS errors
   - Verify Server-Sent Events support

3. **Session Management Issues**
   - Sessions are stored in memory (not persistent)
   - Restarting the service clears all sessions

### **Debug Commands**

```bash
# Check Railway logs
railway logs

# Test locally
python app.py

# Check environment variables
railway variables
```

## 🎯 Next Steps

1. **Deploy**: Push your changes to trigger Railway deployment
2. **Test**: Verify all endpoints are working
3. **Update Frontend**: Integrate streaming chat in your frontend
4. **Monitor**: Watch Railway dashboard for any issues

## 📞 Support

If you encounter issues:
1. Check Railway logs
2. Test endpoints individually
3. Verify environment variables
4. Check the health endpoint

Your streaming chat system is now ready for Railway deployment! 🚀
