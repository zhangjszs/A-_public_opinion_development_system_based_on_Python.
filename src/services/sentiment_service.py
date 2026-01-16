from abc import ABC, abstractmethod
from snownlp import SnowNLP
import requests
import json
import logging
import os
from config.settings import Config

logger = logging.getLogger(__name__)

class SentimentResult:
    """统一的情感分析结果对象"""
    def __init__(self, score, label, reasoning=None, emotion=None, keywords=None):
        self.score = score          # 0-1 float
        self.label = label          # positive/negative/neutral
        self.reasoning = reasoning  # 分析理由 (LLM特有)
        self.emotion = emotion      # 细粒度情感 (喜怒哀乐等)
        self.keywords = keywords    # 关键词列表

    def to_dict(self):
        return {
            'score': self.score,
            'label': self.label,
            'reasoning': self.reasoning,
            'emotion': self.emotion,
            'keywords': self.keywords
        }

class SentimentStrategy(ABC):
    """情感分析策略基类"""
    @abstractmethod
    def analyze(self, text: str) -> SentimentResult:
        pass

class SnowNLPStrategy(SentimentStrategy):
    """基础策略: 使用 SnowNLP (本地/快速)"""
    def analyze(self, text: str) -> SentimentResult:
        if not text:
            return SentimentResult(0.5, 'neutral')
        
        s = SnowNLP(text)
        score = s.sentiments
        
        label = 'neutral'
        if score > 0.6:
            label = 'positive'
        elif score < 0.4:
            label = 'negative'
            
        return SentimentResult(
            score=score,
            label=label,
            keywords=s.keywords(5),
            reasoning="基于文本极性概率计算"
        )

class LLMStrategy(SentimentStrategy):
    """智能策略: 使用 LLM (API/DeepSeek/OpenAI)"""
    def __init__(self):
        self.api_key = os.getenv('LLM_API_KEY')
        self.api_url = os.getenv('LLM_API_URL', 'https://api.deepseek.com/v1/chat/completions')
        self.model = os.getenv('LLM_MODEL', 'deepseek-chat')
        
    def analyze(self, text: str) -> SentimentResult:
        if not self.api_key:
            logger.warning("未配置 LLM_API_KEY，降级使用 SnowNLP")
            return SnowNLPStrategy().analyze(text)
            
        try:
            # 构造 Prompt
            prompt = f"""
            请对以下微博文本进行情感分析。
            文本: "{text}"
            
            请以JSON格式返回结果，包含以下字段:
            - score: 情感得分(0-1之间，1为最积极)
            - label: 情感标签(positive/neutral/negative)
            - emotion: 细粒度情绪(如: 愤怒, 喜悦, 悲伤, 焦虑, 期待, 讽刺, 无感)
            - reasoning: 简短分析理由(50字以内)
            - keywords: 3-5个关键情绪词
            
            只返回JSON，不要包含markdown格式或其他内容。
            """
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            
            result_json = response.json()
            content = result_json['choices'][0]['message']['content']
            
            # 清理可能的 markdown 标记
            content = content.replace('```json', '').replace('```', '').strip()
            
            data = json.loads(content)
            return SentimentResult(
                score=data.get('score', 0.5),
                label=data.get('label', 'neutral'),
                reasoning=data.get('reasoning'),
                emotion=data.get('emotion'),
                keywords=data.get('keywords', [])
            )
            
        except Exception as e:
            logger.error(f"LLM 分析失败: {e}")
            # 失败时降级
            return SnowNLPStrategy().analyze(text)

class CustomModelStrategy(SentimentStrategy):
    """自定义模型策略 (sklearn)"""
    def __init__(self):
        self.model_path = os.path.join(Config.BASE_DIR, 'model', 'best_sentiment_model.pkl')
        self._model = None

    def _load_model(self):
        if self._model is None:
            import joblib
            import sys
            # 添加 model 目录 to sys.path 以便 pickle 可以找到 model_utils
            model_dir = os.path.join(Config.BASE_DIR, 'model')
            if model_dir not in sys.path:
                sys.path.append(model_dir)
            
            # 尝试导入以确保反序列化成功
            try:
                import model_utils
            except ImportError:
                logger.warning("Failed to import model_utils, custom model loading might fail")

            if os.path.exists(self.model_path):
                self._model = joblib.load(self.model_path)
        return self._model

    def analyze(self, text: str) -> SentimentResult:
        model = self._load_model()
        if not model:
            logger.warning("自定义模型未找到，降级使用 SnowNLP")
            return SnowNLPStrategy().analyze(text)

        try:
            # 预测类别
            prediction = model.predict([text])[0]
            # 预测概率 (如果模型支持)
            score = 0.5
            if hasattr(model, "predict_proba"):
                # 获取正类概率 (假设类别顺序 0:负, 1:中, 2:正)
                # 注意: 需要确认模型类别的mapping，这里假设模型输出 0,1,2
                # 如果模型输出是 'positive'/'negative' 字符串，需要相应调整
                # 暂时使用最大概率作为置信度
                probs = model.predict_proba([text])[0]
                score = float(max(probs))
            
            # 映射标签
            # 假设模型训练时的标签是 0:负, 1:中, 2:正
            label_map = {0: 'negative', 1: 'neutral', 2: 'positive'}
            label = label_map.get(prediction, 'neutral')
            
            # 如果预测出来是 int, 尝试转换
            if isinstance(prediction, str):
                # 如果模型直接输出标签字符串
                if prediction in ['positive', 'pos']: label = 'positive'
                elif prediction in ['negative', 'neg']: label = 'negative'
                else: label = 'neutral'

            return SentimentResult(
                score=score,
                label=label,
                reasoning="基于自定义训练模型预测",
                keywords=[] # 自定义模型暂不提取关键词，可结合jieba
            )
        except Exception as e:
            logger.error(f"自定义模型分析失败: {e}")
            return SnowNLPStrategy().analyze(text)

class SentimentService:
    """情感分析服务工厂"""
    
    @staticmethod
    def analyze(text: str, mode: str = 'custom') -> dict:
        """
        执行情感分析
        Args:
            text: 待分析文本
            mode: 模式 'custom'(默认), 'smart'(LLM), 'simple'(SnowNLP)
        """
        if mode == 'smart':
            strategy = LLMStrategy()
        elif mode == 'custom':
             strategy = CustomModelStrategy()
        else:
            strategy = SnowNLPStrategy()
            
        result = strategy.analyze(text)
        return result.to_dict()
