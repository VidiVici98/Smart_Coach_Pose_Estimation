#!/bin/bash
# Create a stub libGL.so.1 to satisfy the dependency

echo "Creating stub libGL.so.1 library..."

# Create a minimal stub library
cat > /tmp/stub.c << 'EOF'
void glXGetProcAddress() {}
void glXQueryExtension() {}
void glXQueryVersion() {}
EOF

gcc -shared -fPIC -o /tmp/libGL.so.1 /tmp/stub.c 2>/dev/null || echo "gcc not available"

# If gcc worked, copy to local lib
if [ -f /tmp/libGL.so.1 ]; then
    mkdir -p ~/.local/lib
    cp /tmp/libGL.so.1 ~/.local/lib/
    export LD_LIBRARY_PATH=~/.local/lib:$LD_LIBRARY_PATH
    echo "✓ Stub library created"
    echo "Run: export LD_LIBRARY_PATH=~/.local/lib:\$LD_LIBRARY_PATH"
else
    echo "gcc not available, trying alternative..."
    # Alternative: Install from deadsnakes or other source
    wget -q http://security.ubuntu.com/ubuntu/pool/main/libg/libglvnd/libgl1_1.3.2-1~ubuntu0.20.04.2_amd64.deb -O /tmp/libgl.deb
    sudo dpkg -i /tmp/libgl.deb 2>/dev/null || sudo apt install -f -y
fi

echo ""
echo "Now run: python3 scripts/processing/run_pipeline.py"
