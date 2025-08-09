import React, { useState, useEffect } from "react";
import { FaBrain, FaFileAlt, FaRobot } from "react-icons/fa";

export default function App() {
  const [summary, setSummary] = useState("");
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [fileList, setFileList] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [context, setContext] = useState("");
  const [score, setScore] = useState(0);
  const [source, setSource] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [qaHistory, setQaHistory] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [predictedCategory, setPredictedCategory] = useState("");


  useEffect(() => {
    fetch("http://127.0.0.1:8000/faiss/list/detailed")
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data.documents)) {
          setFileList(data.documents);
        }
      })
      .catch((err) => console.error("Liste alınamadı", err));
  }, []);

  const handleBulkAsk = async () => {
  if (!question.trim()) {
    setErrorMessage("Lütfen bir soru yazın.");
    return;
  }

  setIsLoading(true);
  setAnswer("");
  setErrorMessage("");

  try {
    const res = await fetch("http://127.0.0.1:8000/multi-qa/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    if (!res.ok) {
      const errorText = await res.text();
      throw new Error("Sunucu hatası: " + errorText);
    }

    const data = await res.json();
    setAnswer(data.answer || "Cevap bulunamadı.");
    setScore(data.score || 0);
    setSource(data.source || "Bilinmiyor");

    setQaHistory((prev) => [
      ...prev,
      {
        question,
        answer: data.answer || "Cevap bulunamadı.",
        score: data.score,
        source: data.source_file,
        context: "", // Bu endpoint context döndürmüyorsa boş geç
      },
    ]);
  } catch (error) {
    console.error("❌ Soru gönderilemedi:", error);
    setErrorMessage("Soru gönderilirken bir hata oluştu: " + error.message);
  } finally {
    setIsLoading(false);
  }
};

const getCategoryColor = (category) => {
  switch (category.toLowerCase()) {
    case "finans":
      return "bg-green-600 text-white";
    case "yapay zeka":
    case "teknik":
    case "yazılım":
      return "bg-blue-600 text-white";
    case "hukuk":
      return "bg-red-600 text-white";
    case "sağlık":
      return "bg-pink-600 text-white";
    default:
      return "bg-gray-500 text-white";
  }
};

const handleFileChange = async (e) => {
  const uploadedFiles = Array.from(e.target.files);
  if (uploadedFiles.length === 0) return;

  const successfullyUploaded = [];

  for (const file of uploadedFiles) {
    const formData = new FormData();
    formData.append("file", file);

    const extension = file.name.split('.').pop().toLowerCase();
    const endpoint = extension === "pdf" ? "upload/pdf" : "upload/html";

    try {
      const res = await fetch(`http://127.0.0.1:8000/${endpoint}`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Yükleme başarısız");
      successfullyUploaded.push(file.name); // Başarılı olanları kaydet

    } catch (error) {
      console.error(`❌ ${file.name} yüklenemedi:`, error);
    }
  }

  // Backend'deki tüm dosyaları çek
  try {
    const listRes = await fetch("http://127.0.0.1:8000/faiss/list/detailed");
    const listData = await listRes.json();
    setFileList(listData.documents || []);
  } catch (err) {
    console.error("Liste güncellenemedi:", err);
  }

  // Yeni yüklenen dosya adlarını seçilenlere ekle
  setSelectedFiles((prev) => [...prev, ...successfullyUploaded]);
};



  const handleAsk = async () => {
    if (!question.trim()) {
      setErrorMessage("Lütfen bir soru yazın.");
      return;
    }

    setIsLoading(true);
    setAnswer("");
    setErrorMessage("");

    try {
    const res = await fetch("http://127.0.0.1:8000/openai-qa/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        filenames: selectedFiles, // Seçili dosya(lar)ı backend'e gönderiyoruz!
      }),
    });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error("Sunucu hatası: " + errorText);
      }

     const data = await res.json();
setAnswer(data.answer || "Cevap bulunamadı.");
setScore(data.score || 0);
setSource(data.source || "Bilinmiyor");
setPredictedCategory(data.predicted_category || "Bilinmiyor");

      setQaHistory((prev) => [
        ...prev,
        {
          question,
          answer: data.answer || "Cevap bulunamadı.",
          score: data.score,
          source: data.source_file,
          context: data.context,
        },
      ]);
    } catch (error) {
      console.error("❌ Soru gönderilemedi:", error);
      setErrorMessage("Soru gönderilirken bir hata oluştu: " + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (filename) => {
    if (!window.confirm(`\"${filename}\" dosyasını silmek istiyor musunuz?`)) return;

    try {
      const res = await fetch(`http://127.0.0.1:8000/faiss/delete/${filename}`, {
        method: "DELETE",
      });

      if (!res.ok) throw new Error("Silme başarısız");

      const listRes = await fetch("http://127.0.0.1:8000/faiss/list/detailed");
      const listData = await listRes.json();
      setFileList(listData.documents || []);

      setSuccessMessage(`\"${filename}\" başarıyla silindi.`);
      setTimeout(() => setSuccessMessage(""), 2500);
    } catch (error) {
      console.error("❌ Dosya silinemedi:", error);
    }
  };
  const handleMultiAsk = async () => {
  if (!question.trim()) {
    setErrorMessage("Lütfen bir soru yazın.");
    return;
  }

  setIsLoading(true);
  setAnswer("");
  setErrorMessage("");
  setSummary("");
  setContext("");
  setScore(0);
  setSource("");

  try {
    const res = await fetch("http://127.0.0.1:8000/multi-qa/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    if (!res.ok) throw new Error("Sunucu hatası");

    const data = await res.json();
    setAnswer(data.answer || "Cevap bulunamadı.");
    setScore(data.score || 0);
    setSource(data.source || "Bilinmiyor");

    setQaHistory((prev) => [
      ...prev,
      {
        question,
        answer: data.answer || "Cevap bulunamadı.",
        score: data.score,
        source: data.source,
        context: "",
      },
    ]);
  } catch (error) {
    console.error("❌ Soru gönderilemedi:", error);
    setErrorMessage("Toplu soru gönderimi başarısız: " + error.message);
  } finally {
    setIsLoading(false);
  }
};


  return (
    <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center p-4">
      <div className="w-full max-w-xl space-y-6">
        <div className="flex items-center space-x-3 justify-center">
          <FaBrain className="text-pink-400 text-4xl" />
          <h1 className="text-4xl font-bold">AI Doc Reader</h1>
        </div>

        <div className="flex items-center bg-gray-800 border border-gray-700 rounded-xl p-4 space-x-3">
          <FaFileAlt className="text-white text-2xl" />
          <span className="flex-1 truncate">
  {selectedFiles.length > 0
    ? selectedFiles.map((file, idx) => (
        <span key={idx}>
          {typeof file === "string"
            ? file
            : file.name || file.filename || "isimsiz"}
          {idx !== selectedFiles.length - 1 && ", "}
        </span>
      ))
    : "Henüz dosya seçilmedi"}
</span>

          <label className="bg-blue-600 hover:bg-blue-700 text-white py-1 px-4 rounded-lg cursor-pointer">
            Dosya Yükle
            <input type="file" accept=".html,.pdf" multiple className="hidden" onChange={handleFileChange} />
          </label>
        </div>

        <input
  type="text"
  placeholder="Sorunuzu yazın..."
  value={question}
  onChange={(e) => {
    setQuestion(e.target.value);
    setErrorMessage("");
  }}
  className="w-full bg-gray-800 text-white p-4 rounded-xl border border-gray-700 outline-none"
/>

{/* Seçili dosya bilgisi (çoklu dosya) */}
{selectedFiles.length > 0 && (
  <p className="text-sm text-gray-400 mt-2">
    Soru şu dosyalar üzerinden sorulacak: <strong>{selectedFiles.join(", ")}</strong>
  </p>
)}

{/* Soru Sor butonu */}
<div className="flex justify-end">
  <div className="flex justify-end space-x-3">
    <button
      onClick={handleAsk}
      className="mt-2 flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition"
    >
      <FaRobot />
      <span>Soru Sor</span>
    </button>
  </div>
</div>

{/* Hata mesajı varsa göster */}
{errorMessage && (
  <div className="bg-red-600 text-white p-3 rounded-xl text-sm font-medium mt-2">
    {errorMessage}
  </div>
)}


        {successMessage && (
          <div className="bg-green-600 text-white p-3 rounded-xl text-sm font-medium">
            {successMessage}
          </div>
        )}

        {isLoading ? (
          <div className="bg-gray-800 text-blue-400 p-4 rounded-xl border border-gray-700 italic">
            Cevap hazırlanıyor...
          </div>
        ) : (
          answer && (
            <>
              <div className="mt-4 p-4 border rounded-lg shadow bg-gray-800 text-white space-y-2">
      <p>
        <strong>Tahmin Edilen Kategori:</strong>{" "}
        <span className={`px-2 py-1 rounded ${getCategoryColor(predictedCategory)}`}>
          {predictedCategory}
        </span>
      </p>
      <p><strong>Cevap:</strong> {answer}</p>
      
      {score < 0.3 && (
        <p className="text-yellow-400 text-sm">
          Bu cevap düşük güven puanına sahip olabilir.
        </p>
      )}

      <p className="text-sm text-gray-400">
        | Güven Skoru: {Math.round(score * 100)}%
      </p>

      
                </div>

              {summary && (
                <div className="bg-gray-800 text-gray-300 p-4 rounded-xl border border-gray-700 space-y-2">
                  <p><strong>Özet:</strong> {summary}</p>
                </div>
              )}
            </>
          )
        )}

        {qaHistory.length > 0 && (
          <div className="space-y-4 mt-6">
            <h2 className="text-xl font-semibold border-b pb-1 border-gray-700">Önceki Sorular</h2>
            {qaHistory.map((item, idx) => (
              <div key={idx} className="bg-gray-800 p-4 rounded-xl border border-gray-700 space-y-2">
                <p><strong>Soru:</strong> {item.question}</p>
                <p><strong>Cevap:</strong> {item.answer}</p>
                {item.score < 0.3 && (
                  <p className="text-yellow-400 text-sm">Bu cevap düşük güven puanına sahip olabilir.</p>
                )}
                <p className="text-sm text-gray-400">
                  Kaynak: {item.source} | Güven Skoru: {Math.round(item.score * 100)}%
                  {item.context === "" && " | 🔁 Toplu doküman taraması"}
                </p>
                
              </div>
            ))}
          </div>
        )}

        <ul className="space-y-2">
  {(fileList ?? []).map((doc, idx) => {
    const isSelected = selectedFiles.includes(doc.filename);

    return (
      <li
        key={idx}
        onClick={() => {
          if (isSelected) {
            setSelectedFiles((prev) => prev.filter((f) => f !== doc.filename));
          } else {
            setSelectedFiles((prev) => [...prev, doc.filename]);
          }
        }}
        className={`bg-gray-700 p-3 rounded-xl cursor-pointer border transition ${
          isSelected ? "border-green-500" : "border-transparent"
        }`}
      >
        <div className="flex justify-between items-center mb-1">
          <span className="font-semibold">{doc.filename}</span>
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleDelete(doc.filename);
            }}
            className="text-red-400 hover:text-red-600 transition"
          >
            Sil
          </button>
        </div>
        <p className="text-sm text-gray-400">
          Tür: {doc.filetype} | Karakter: {doc.char_count} | Yüklendi: {doc.uploaded_at?.slice(0, 19).replace('T', ' ') || "N/A"}
        </p>
        <p className="text-sm text-gray-300 mt-1 italic">“{doc.preview}”</p>
      </li>
    );
  })}
</ul>
      </div>
    </div>
  );
}