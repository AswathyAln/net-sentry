FROM python:3.9-slim
RUN apt-get update && apt-get install -y libpcap-dev tcpdump && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
RUN echo '#!/bin/bash\npython3 scanner.py & streamlit run dashboard.py --server.port=8501 --server.address=0.0.0.0' > start.sh
RUN chmod +x start.sh
CMD ["./start.sh"]
