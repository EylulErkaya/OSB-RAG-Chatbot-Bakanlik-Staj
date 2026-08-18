\# OSB RAG Chatbot



Organize Sanayi Bölgelerine (OSB) ait verilerin doğal dil ile sorgulanabilmesini

sağlamak amacıyla geliştirilen RAG (Retrieval-Augmented Generation) tabanlı

chatbot projesidir.



\## Proje Amacı



Excel formatında bulunan OSB verilerinin analiz edilmesi, temizlenmesi,

normalize edilmesi, dokümanlara ve chunk'lara dönüştürülmesi ve embedding

tabanlı retrieval sistemi içerisinde kullanılabilir hale getirilmesi

amaçlanmaktadır.



\## Mevcut Durum



\- Excel veri analizi

\- Veri temizleme

\- Veri normalizasyonu

\- Veri doğrulama

\- Veri sözlüğü oluşturma

\- RAG dokümanlarının oluşturulması

\- Chunking

\- Chunk validation

\- Embedding oluşturma

\- Retrieval testleri



tamamlanmıştır.



\## Veri Yapısı



Proje kapsamında:



\- 500 OSB kaydı

\- 12.000 sektör kaydı

\- 12.500 RAG dokümanı

\- 13.514 bilgi chunk'ı



oluşturulmuştur.



\## Embedding



Embedding işlemlerinde:



\- Model: `nomic-embed-text:v1.5`

\- Embedding boyutu: 768

\- Embedding sayısı: 13.514



kullanılmıştır.



\## Teknolojiler



\- Python

\- Pandas

\- OpenPyXL

\- Ollama

\- Nomic Embed Text

\- RAG

\- Vector Database

\- GroqCloud



\## Proje Yapısı



```text

OSB-RAG-Chatbot/

├── src/

├── data/

├── .gitignore

├── requirements.txt

└── README.md

