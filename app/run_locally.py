if __name__ == '__main__':
    import uvicorn
    uvicorn.run('api.main:app', host='0.0.0.0', port=8880, reload=True)