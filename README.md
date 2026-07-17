# 🌅 DayForge — AI Morning Brief Agent

An autonomous AI-powered agent that wakes up at 6 AM every day, gathers weather, GitHub activity & news, synthesizes a personalized morning brief using Amazon Bedrock, and delivers it to your inbox before you open your eyes.

**Zero human interaction needed. Fully serverless. Always on.**

Built for the **AWS Builder Challenge: Build an Always-On Agent**.

---

## 🎯 What It Does

Every morning at 6 AM (automatically):
1. ☁️ Fetches weather for your city
2. 💻 Scans GitHub for overnight activity
3. 📰 Pulls top news headlines
4. 🧠 Invokes Amazon Bedrock (Nova Micro) to synthesize a personalized brief
5. 📧 Emails you the result via Amazon SES
6. 💾 Stores the brief in DynamoDB for history

---

## 🏗️ Architecture
ventBridge Scheduler (6 AM daily) │ ▼ AWS Lambda (Python 3.11) │ ├── Weather API (OpenWeatherMap) ├── GitHub API (user activity) ├── News API (headlines) │ ▼ Amazon Bedrock (Nova Micro) "Synthesize morning brief" │ ├── SES → Email delivery └── DynamoDB → Brief storage


---

## 🛠️ AWS Services Used (All Free Tier)

| Service | Purpose |
|---------|---------|
| **AWS Lambda** | Agent execution |
| **Amazon Bedrock** | AI brief generation |
| **EventBridge** | Cron scheduling |
| **DynamoDB** | Brief history storage |
| **SES** | Email delivery |
| **CloudWatch** | Logging & monitoring |
| **AWS CDK** | Infrastructure as Code |

---

## 🚀 Deploy

```bash
git clone https://github.com/YOUR_USERNAME/dayforge.git
cd dayforge
cp .env.example .env
# Edit .env with your API keys

cd cdk
pip install -r requirements.txt
cdk bootstrap
cdk deploy
⚙️ Configuration
Edit .env:

CITY=New York
GITHUB_USERNAME=your-username
GITHUB_TOKEN=ghp_xxxxx
OPENWEATHER_API_KEY=xxxxx
NEWS_API_KEY=xxxxx
EMAIL_TO=you@email.com
EMAIL_FROM=you@email.com
🧪 Test Manually
aws lambda invoke --function-name DayForgeAgent --payload '{}' output.json
cat output.json
📧 Sample Brief
☀️ Good morning!

🌤️ WEATHER — New York
72°F, partly cloudy. High of 81°F. Bring sunglasses!

💻 GITHUB
2 new PRs (1 ready for review). Issue #42 got 3 comments.

📰 TOP STORIES
• AWS announces new Bedrock features
• Python 3.13 RC available
• Tech industry hiring update

🎯 TODAY'S FOCUS
You have PRs to review and a clear morning — ideal for deep work.

Have a great day! ☕
🏆 Challenge Requirements Met
Requirement	Status
AI-powered agent	✅ Amazon Bedrock
Runs on its own	✅ EventBridge cron
No user interaction needed	✅ Fully autonomous
Does something useful while away	✅ Gathers & synthesizes data
Result ready when you return	✅ Email in inbox
AWS Free Tier	✅ All services
📝 License
MIT

