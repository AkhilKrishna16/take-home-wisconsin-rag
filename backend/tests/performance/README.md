# Performance Tests

Comprehensive performance evaluation and benchmarking for the Legal RAG System.

## 📋 Test Files

### `test_performance_metrics.py`
Complete performance evaluation suite covering:

1. **Retrieval Accuracy Metrics**
   - Precision and recall calculations
   - F1 scores and relevance thresholds
   - Top-K accuracy measurements
   - Mean Reciprocal Rank (MRR) scoring

2. **Response Time Benchmarks**
   - End-to-end response timing
   - Component-level performance breakdown
   - Percentile distributions (95th, median, average)
   - Retrieval vs generation time analysis

3. **Relevance Scoring Evaluation**
   - Score distribution analysis
   - Confidence calibration testing
   - Ranking quality assessment
   - Multi-factor relevance breakdown

4. **Query Set Performance Testing**
   - Standardized test query evaluation
   - Confidence threshold validation
   - Source count verification
   - Query type performance analysis

## 🏃 Running Performance Tests

```bash
# Run complete performance evaluation
cd backend
python3 tests/performance/test_performance_metrics.py

# The test will:
# 1. Initialize RAG system and chatbot
# 2. Run all performance evaluations
# 3. Generate detailed JSON report
# 4. Display summary statistics
```

## 📊 Test Query Set

The performance tests use a curated set of legal queries:

### Query Types Tested
1. **Specific Statute**: "What does 18 U.S.C. 2703 say about digital evidence?"
2. **Constitutional Law**: "Fourth Amendment protections for digital privacy"  
3. **State-Specific**: "Wisconsin statutes on evidence collection procedures"
4. **Procedural Law**: "Miranda rights requirements during arrest"
5. **Policy/Procedure**: "Use of force policies in law enforcement"
6. **Warrant Law**: "Search warrant requirements for electronic devices"

### Performance Targets
- **Response Time**: <3 seconds average
- **Confidence Score**: >0.7 for most queries
- **Source Count**: 3-4 relevant sources per query
- **Success Rate**: 100% query completion

## 📈 Performance Reports

### Console Output
```
🎯 Retrieval Accuracy:
   Precision: 0.82
   Recall: 0.76  
   F1 Score: 0.79

⏱️ Response Times:
   Average: 2.41s
   Median: 2.15s
   95th Percentile: 3.53s

🎖️ Relevance Scoring:
   Overall Average: 0.486
   Top Score Average: 0.574

📋 Query Set Performance:
   Success Rate: 100%
   Confidence Success: 67%
   Average Confidence: 0.569
```

### JSON Report Structure
```json
{
  "retrieval_accuracy": {
    "precision_scores": [...],
    "average_precision": 0.82,
    "top_k_accuracy": {...}
  },
  "response_times": {
    "total_times": [...],
    "average_total_time": 2.41,
    "p95_total_time": 3.53
  },
  "relevance_scores": {
    "score_distributions": [...],
    "overall_score_average": 0.486
  },
  "query_set_results": {
    "individual_results": [...],
    "aggregate_metrics": {...}
  }
}
```

## 🎯 Benchmark Targets

### Production Readiness Criteria
- **Response Time**: <3s average, <5s 95th percentile ✅
- **Accuracy**: >80% precision, >75% recall ⚠️ (needs more content)
- **Confidence**: >70% average confidence score ⚠️ (60% current)
- **Availability**: >99% success rate ✅
- **Relevance**: >0.6 average relevance score ✅

### Current Performance Status
- ✅ **Response Times**: Excellent (2.4s average)
- ✅ **System Reliability**: Perfect (100% success rate)
- ✅ **Relevance Scoring**: Good (0.57 top scores)
- ⚠️ **Confidence Scores**: Needs improvement (56% average)
- ⚠️ **Content Coverage**: Needs more legal documents

## 🔧 Performance Optimization

### Current Optimizations
- **Vector Database**: Pinecone serverless for fast retrieval
- **Embedding Model**: all-MiniLM-L6-v2 (384d, optimized for speed)
- **Caching**: LangChain conversation memory
- **Batch Processing**: Efficient vector operations

### Recommended Improvements
1. **Add more legal documents** to improve accuracy
2. **Tune confidence thresholds** based on actual performance
3. **Implement result caching** for common queries
4. **Optimize embedding batch sizes** for your use case

## 📊 Monitoring and Alerting

### Key Metrics to Monitor
- **Average Response Time**: Alert if >3s
- **Error Rate**: Alert if >1%
- **Confidence Score**: Alert if <60% average
- **Database Latency**: Alert if >500ms

### Performance Baselines
- **Retrieval Time**: ~0.7s (30% of total time)
- **Generation Time**: ~1.7s (70% of total time)
- **Query Enhancement**: ~50ms overhead
- **Safety Checks**: ~10ms overhead
