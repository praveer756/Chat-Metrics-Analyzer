# 💬 Chat Metrics Analyzer

**Production-grade WhatsApp chat analytics dashboard built with Python and Streamlit.**

Analyze WhatsApp chat exports to uncover communication patterns, participant behavior, and conversation insights. Perfect for understanding group dynamics or personal messaging habits.

---

## 🎯 Problem Statement

WhatsApp doesn't provide analytics on your chat data. This project extracts actionable insights from your exported chats:
- **Who's the most active?** Identify conversation leaders
- **When do people chat most?** Find activity patterns by time/day/month
- **What's the conversation sentiment?** Analyze positivity/negativity trends over time
- **Are there anomalies?** Detect unusual message spikes
- **What are people talking about?** Wordcloud and common words analysis

---

## ✨ Features

### Current (Phase 2)
- ✅ **Upload & Parse** - Support for standard WhatsApp TXT exports (Android/iOS/Web)
- ✅ **Real-time Statistics** - Total messages, words, media, links
- ✅ **Activity Timeline** - Monthly and daily message trends
- ✅ **Activity Maps** - Heatmaps showing when people chat most (by day/hour/month)
- ✅ **User Ranking** - See who contributes most to the group
- ✅ **Wordcloud Visualization** - Most frequently used words (with stopword filtering)
- ✅ **Per-User Analysis** - Slice insights by individual participant
- ✅ **Sentiment Trend Analysis** - Daily positive/neutral/negative trend
- ✅ **Anomaly Detection** - Isolation Forest based unusual activity detection
- ✅ **Time-Series Decomposition** - Trend, seasonality, and residual breakdown

### Planned (Next)
- 🚀 CI/CD pipeline (GitHub Actions)
- 🚀 Deployment guide with live demo link

---

## 🛠️ Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| **Backend Logic** | Python 3.10+ | Industry standard for data analysis |
| **Web Framework** | Streamlit 1.39+ | Zero-config interactive dashboards |
| **Data Processing** | Pandas 2.2+ | Best-in-class DataFrame operations |
| **Visualization** | Matplotlib + Seaborn | Publication-quality charts |
| **Text Processing** | NLTK, URLExtract, Emoji | Robust text analytics |
| **Deployment** | Streamlit Cloud / Docker | Scalable cloud-ready app |

---

## 📋 Requirements

- **Python**: 3.10 or higher
- **OS**: Windows, macOS, Linux
- **RAM**: 2GB minimum (for typical chats)

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/chat-metrics-analyzer.git
cd Chat-Metrics-Analyzer
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Locally
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 📱 How to Use

### Export WhatsApp Chat

1. **Open WhatsApp** (Android, iOS, or Web)
2. **Select a chat** (group or individual)
3. **More options** → **Export Chat** 
4. **Choose "Without Media"** (faster upload)
5. **Save as TXT file**

### Upload to Analyzer

1. Click **"Choose a file"** in the sidebar
2. Select your exported `.txt` file
3. Choose a user from the dropdown (or "Overall" for entire chat)
4. Click **"Show Analysis"** button
5. Explore all visualizations!

---

## 📊 Example Insights You Can Extract

```
Total Messages: 2,847
Total Words: 19,234
Media Shared: 156
Links Shared: 34

Most Active User: Alex (32% of messages)
Most Common Words: lol, thanks, yeah, sure, meeting
Most Active Day: Friday
Most Active Time: 8-10 PM

Sentiment Trend: Increasingly positive over past 3 months
Anomalies: 5 unusual spikes in activity detected
```

---

## 🏗️ Project Structure

```
Chat-Metrics-Analyzer/
├── app.py                  # Main Streamlit application
├── config.py              # Configuration constants
├── preprocessor.py        # WhatsApp data parsing & validation
├── analytics.py           # Statistical analysis functions
├── requirements.txt       # Python dependencies
├── .gitignore            # Git configuration
├── README.md             # This file
└── stop_hinglish.txt     # Stopwords for Hinglish (optional)
```

### Code Quality
- ✅ **Type Hints**: Full Python 3.10+ type annotations
- ✅ **Docstrings**: Comprehensive function documentation
- ✅ **Logging**: Built-in debug/info logging
- ✅ **Error Handling**: Graceful error messages for users
- ✅ **Caching**: `@st.cache_data` for performance optimization

---

## 📝 Configuration

All constants are centralized in `config.py`:

```python
# Adjust these for your needs:
CACHE_TTL_SECONDS = 3600      # How long to cache processed data
WORDCLOUD_WIDTH = 500          # Wordcloud size
WORDCLOUD_HEIGHT = 500
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **"Could not parse WhatsApp format"** | Ensure file is exported from WhatsApp, not manually created. Try "Without Media" export option. |
| **"Module not found: X"** | Run `pip install -r requirements.txt` again |
| **Slow performance** | Reduce data size or use Streamlit Cloud (has better resources) |
| **Empty wordcloud** | Chat may have only media/system messages. Try analyzing specific user. |

---

## 🔒 Privacy & Security

- **Data stays local**: All processing happens on your machine (no uploads to internet)
- **No storage**: Data is not saved after analysis ends
- **File handling**: Only read-only access to uploaded files
- **Recommendations**: Don't share your exported chat files with strangers (they contain personal messages!)

---

## 🧪 Testing

Run the test suite:
```bash
 python -m pytest tests/ -v
```

---

## 📚 Key Functions Reference

### `preprocessor.py`
- `preprocess(data: str) → pd.DataFrame` - Parse WhatsApp export
- `validate_dataframe(df: pd.DataFrame) → None` - Data integrity checks

### `analytics.py`
- `fetch_stats(user, df)` - Get basic statistics
- `activity_heatmap(user, df)` - Generate day/hour activity matrix
- `create_wordcloud(user, df)` - Generate wordcloud
- `most_common_words(user, df)` - Extract top words
- `emoji_helper(user, df)` - Analyze emoji usage
- `most_busy_users(df)` - Rank participants by message count
- `sentiment_over_time(user, df)` - Daily sentiment trend
- `detect_message_anomalies(user, df)` - Isolation Forest anomaly detection
- `decompose_daily_messages(user, df)` - Time-series decomposition

See docstrings in code for full parameter details.

---

## 📈 Performance Tips

1. **Use "Without Media" exports** - Significantly smaller files
2. **Analyze by user** - Faster than "Overall" for large groups
3. **Cache is automatic** - Same file re-analyzed instantly
4. **Sampling** - For 50k+ messages, consider subsetting by date range

---

## 🤝 Contributing

Found a bug or have ideas? Please open an Issue or Pull Request!

### Development Setup
```bash
pip install pytest black pylint
black app.py preprocessor.py analytics.py  # Format code
pylint app.py                         # Lint code
pytest tests/                         # Run tests
```

---

## 📖 Learning Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Pandas User Guide](https://pandas.pydata.org/docs/)
- [WhatsApp Chat Export Formats](https://www.whatsapp.com/faq)

---

## ⚠️ Limitations & Known Issues

1. **iOS exports**: Only supported if exported from mobile (web export may differ)
2. **Deleted messages**: Show as incomplete lines; may affect analysis slightly
3. **Chat backups**: Restoring from backup before export can cause duplicates
4. **Large files**: >100k messages may take 30+ seconds to process
5. **Emojis**: On older Python versions, emoji display may be inconsistent
6. **Multi-language**: Stopwords are Hinglish-specific; add your language's stopwords to `stop_hinglish.txt`

---

## 🎓 What This Project Demonstrates

### For Data Analyst Interviews
✅ End-to-end data pipeline (load → clean → analyze → visualize)  
✅ Real-world data quality issues (formatting, edge cases)  
✅ Statistical thinking (aggregation, grouping, trends)  
✅ User-centric design (error messages, documentation)  

### For Software Engineering Interviews
✅ Production code practices (types, logging, tests)  
✅ Modular architecture (separation of concerns)  
✅ Configuration management  
✅ Caching and performance optimization  

### For ML/Analytics Interviews
✅ Sentiment analysis with transformer-first fallback strategy  
✅ Time-series anomaly detection using Isolation Forest  
✅ Seasonal decomposition for trend intelligence  

---

## 📄 License

This project is open source. Use it however you'd like!

---

## 🙋 FAQ

**Q: Can I use this to spy on someone?**  
A: No. You can only analyze chats YOU have access to. It's for personal insights!

**Q: Will this store my data?**  
A: No. Everything happens locally. No data is sent to any server.

**Q: How accurate is the analysis?**  
A: Very! We parse the official WhatsApp export format. Only limitation is deleted/system messages.

**Q: Can I analyze SMS instead of WhatsApp?**  
A: Not yet. Would require SMS parser (future feature).

**Q: What about group admin insights?**  
A: That's coming in Phase 3 (once we add more advanced features).

---

## 📞 Support

- 📧 Email: guptapraveer3834@gmail.com
- 💬 Issues: Open a GitHub issue
- 🐦 Instagram: @praveer_42

---

**Made with ❤️ in Python | Last updated: March 2026**
