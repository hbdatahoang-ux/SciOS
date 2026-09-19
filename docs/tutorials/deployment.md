# Deployment Guide - SciOS-NG

## 📖 Introduction
Hướng dẫn này mô tả cách triển khai **SciOS-NG** trong các môi trường khác nhau.  
Mục tiêu: đảm bảo hệ thống được triển khai **ổn định, tái lập, và an toàn**.

---

## 🛠️ Prerequisites
- **Docker** hoặc **Kubernetes** để quản lý container.  
- **Git** để clone repository.  
- **CI/CD pipeline** (GitHub Actions, GitLab CI, Azure DevOps).  
- Quyền truy cập vào **[kernel API](ca://s?q=Kernel_API_contract)** và **[runtime API](ca://s?q=Runtime_API_contract)**.  

---

## 🚀 Deployment Steps

### 1. Clone Repository
```bash
git clone https://github.com/scios-ng/scios-ng.git
cd scios-ng
