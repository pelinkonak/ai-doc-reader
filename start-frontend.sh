#!/bin/bash

echo "📦 Frontend başlatılıyor..."
cd frontend || {
  echo "❌ 'frontend' klasörü bulunamadı."
  exit 1
}

npm run dev
