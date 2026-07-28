docker network ls
docker run -d --name wvr-lite --network mcp_mcp-network -p 8080:8080 wvr-lite