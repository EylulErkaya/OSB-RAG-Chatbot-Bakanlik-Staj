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

````text

OSB-RAG-Chatbot/

├── src/

├── data/

├── .gitignore

├── requirements.txt

└── README.md

## TODO - Conversation Session State

Şu anda RAGPipeline içerisinde:

- `pending_query`
- `pending_candidates`

instance-level state olarak tutulmaktadır.

Bu yapı tek kullanıcılı CLI/test aşaması için uygundur.

### FastAPI aşamasında yapılacaklar

API çok kullanıcılı hale geldiğinde ambiguous state kullanıcılar arasında paylaşılmamalıdır.

Yapılacaklar:

1. `ask()` metoduna `session_id` eklenmesi.
2. Pending state'in session bazlı tutulması.
3. Örneğin:
   `dict[session_id, PendingState]`
4. Her kullanıcının kendi:
   - pending query
   - pending candidates
   state'ine sahip olması.
5. Gerekirse state'in Redis veya başka bir dış storage'a taşınması.

Örnek hedef yapı:

```text
session_id
    ↓
PendingState
    ├── query
    └── candidates
````
