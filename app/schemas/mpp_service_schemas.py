from typing import Optional

from pydantic import BaseModel


class ServiceBase(BaseModel):
    jenis_instansi: Optional[str] = None
    nama_layanan: Optional[str] = None
    deskripsi_singkat: Optional[str] = None
    instansi_penyelenggara: Optional[str] = None
    persyaratan: Optional[str] = None
    waktu_penyelesaian: Optional[str] = None
    tarif_pelayanan: Optional[str] = None
    prosedur: Optional[str] = None
    produk_layanan: Optional[str] = None
    pengaduan: Optional[str] = None
    dasar_hukum: Optional[str] = None
    sarana_prasarana: Optional[str] = None
    komponen_pelaksana: Optional[str] = None
    pengawasan_internal: Optional[str] = None
    jumlah_pelaksana: Optional[str] = None
    jaminan_pelayanan: Optional[str] = None
    jaminan_keamanan: Optional[str] = None

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(ServiceBase):
    pass

class Service(ServiceBase):
    id: str
    created_at: Optional[str] = None