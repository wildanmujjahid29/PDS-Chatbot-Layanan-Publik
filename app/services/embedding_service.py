import re

import numpy as np
from chonkie import AutoEmbeddings

# Pilih model
# embeddings = AutoEmbeddings.get_embeddings("all-MiniLM-L6-v2")         # 384 dimensi
embeddings = AutoEmbeddings.get_embeddings("minishlab/potion-base-32M")  # 512 dimensi

def join_service_content_with_labels(service) -> str:
    """
    Gabungkan field layanan dalam format natural language tanpa label.
    Format lebih natural agar embedding lebih baik dan mudah dipahami LLM.
    """
    parts = []
    
    # Nama layanan (paling penting, di awal)
    if service.nama_layanan:
        parts.append(service.nama_layanan)
    
    # Deskripsi singkat (tambahan baru, penting untuk overview)
    if service.deskripsi_singkat:
        parts.append(service.deskripsi_singkat)
    
    # Instansi penyelenggara
    if service.instansi_penyelenggara:
        parts.append(f"Diselenggarakan oleh {service.instansi_penyelenggara}")
    
    # Persyaratan
    if service.persyaratan:
        parts.append(f"Persyaratan yang diperlukan: {service.persyaratan}")
    
    # Waktu dan Tarif
    if service.waktu_penyelesaian:
        parts.append(f"Waktu penyelesaian: {service.waktu_penyelesaian}")
    if service.tarif_pelayanan:
        parts.append(f"Biaya: {service.tarif_pelayanan}")
    
    # Prosedur
    if service.prosedur:
        parts.append(f"Prosedur: {service.prosedur}")
    
    # Produk layanan
    if service.produk_layanan:
        parts.append(f"Hasil layanan: {service.produk_layanan}")
    
    # Pengaduan
    if service.pengaduan:
        parts.append(f"Informasi pengaduan: {service.pengaduan}")
    
    # Join dengan spasi (lebih natural)
    return ". ".join(parts) + "."

def preprocess_text(text: str) -> str:
    # Lowercase
    text = text.lower()
    # Hilangkan karakter non-alfanumerik kecuali beberapa tanda baca
    text = re.sub(r"[^a-z0-9,.:;()\-\n| ]+", "", text)
    # Hilangkan spasi berlebih
    text = re.sub(r"\s+", " ", text)
    # Strip di ujung
    text = text.strip()
    return text

def generate_embedding(content: str) -> list[float]:
    return embeddings.embed(content).tolist()

def normalize_vector(vec: list[float]) -> list[float]:
    arr = np.array(vec)
    norm = np.linalg.norm(arr)
    if norm == 0:
        return arr.tolist()
    return (arr / norm).tolist()

def pipeline_embedding(service) -> tuple[str, list[float]]:
    raw_content = join_service_content_with_labels(service)
    processed_content = preprocess_text(raw_content)
    emb_vector = generate_embedding(processed_content)
    emb_vector_norm = normalize_vector(emb_vector)
    return processed_content, emb_vector_norm