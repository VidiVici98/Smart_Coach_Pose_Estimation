# Quick Start Card - Mobile User Edition

## 🚀 Fastest Path to Success

### Option 1: Cloud Processing (RECOMMENDED for Mobile)
**Time:** 15 minutes | **Cost:** Free

```bash
# 1. On github.com (mobile browser):
   - Open repository
   - Click "Code" → "Codespaces" → "Create codespace"

# 2. In Codespace terminal:
bash scripts/tools/setup.sh
python scripts/tools/create_test_video.py
python scripts/processing/run_pipeline.py

# 3. Download results from Codespace to mobile
```

**Why?** GPU acceleration, fast downloads, no battery drain on your device.

---

### Option 2: Local Mobile Setup (Advanced Users)
**Time:** 60+ minutes | **Only for:** Short test clips

```bash
# Install Termux (Android) or iSH (iOS) first

# Then:
git clone https://github.com/VidiVici98/Smart_Coach_Pose_Estimation.git
cd Smart_Coach_Pose_Estimation
bash scripts/tools/setup.sh
python scripts/tools/create_test_video.py
python scripts/processing/run_pipeline.py
```

**Warning:** Will take 30-60 minutes to process a 10-second video on mobile.

---

## 📚 Essential Documentation

| What You Need | Read This |
|---------------|-----------|
| First time setup | `docs/guides/SETUP.md` |
| Mobile workflow | `MOBILE_WORKFLOW.md` ⭐ |
| Problems/errors | `docs/troubleshooting/TROUBLESHOOTING.md` |
| Project overview | `README.md` |
| What changed | `RECOVERY_SUMMARY.md` |

**On mobile terminal:**
```bash
cat MOBILE_WORKFLOW.md | less
```

---

## ⚡ Quick Commands

```bash
# Check what's installed/missing
python scripts/tools/verify_setup.py

# Activate virtual environment
source mediapipe_env/bin/activate

# Create test video
python scripts/tools/create_test_video.py

# Run the pipeline
python scripts/processing/run_pipeline.py

# Check results
ls -lh data/output/
```

---

## 🎯 What You Should Do NOW

### If You're on Mobile RIGHT NOW:

1. **Read the mobile workflow guide:**
   ```bash
   cat MOBILE_WORKFLOW.md | less
   ```

2. **Check repository status:**
   ```bash
   python scripts/tools/verify_setup.py
   ```

3. **Decide your approach:**
   - Processing videos? → Use cloud (Codespaces/Colab)
   - Just exploring? → Continue on mobile
   - Making small edits? → Perfect for mobile

4. **Follow the recommended workflow:**
   - See MOBILE_WORKFLOW.md Section: "Workflow 3: Hybrid"

---

## 🔧 If Something Goes Wrong

1. **Check troubleshooting guide:**
   ```bash
   cat TROUBLESHOOTING.md | less
   ```

2. **Common mobile issues:**
   - Storage full → Delete old files, use external SD
   - Battery drain → Connect to charger or use cloud
   - Slow install → Let it run overnight, or use cloud
   - Can't type commands → Create shell scripts

3. **Get help:**
   - All answers in `TROUBLESHOOTING.md`
   - Each data directory has README with guidance

---

## ✅ Success Criteria

You're ready to go when:
- [ ] You've read MOBILE_WORKFLOW.md
- [ ] You've chosen cloud or local processing
- [ ] You understand the time/storage requirements
- [ ] You know where to find help (TROUBLESHOOTING.md)

---

## 📱 Mobile-Specific Tips

**Storage:** 
- Repo: ~100 MB
- Dependencies: ~500 MB
- Models: ~85 MB
- Total: ~700 MB minimum

**Time:**
- Clone repo: 2 min
- Install deps: 20-30 min
- Download models: 5 min
- Process 10-sec video: 30-60 min

**Battery:**
- Setup: Moderate drain
- Processing: Heavy drain (connect to power!)

**Network:**
- Initial setup: 600 MB
- Model downloads: 85 MB
- Use WiFi for initial setup

---

## 🎓 Next Steps

1. **Read MOBILE_WORKFLOW.md** (12 KB, essential reading)
2. **Choose your workflow** (Cloud recommended)
3. **Follow the steps** (documented for each workflow)
4. **Get results!**

---

## 💡 Pro Tips

- **Use cloud for processing, mobile for analysis**
- **Create shell script shortcuts for common commands**
- **Keep documentation open in second terminal tab**
- **Process overnight on charger if using local**
- **Start with 5-second test clips**

---

## 🆘 Emergency Help

**Something broken?**
```bash
cat TROUBLESHOOTING.md | grep -A 10 "your error message"
```

**Need to start over?**
```bash
rm -rf mediapipe_env
bash scripts/tools/setup.sh
```

**Still stuck?**
- Check `TROUBLESHOOTING.md`
- Read relevant README in data directories
- Review `MOBILE_WORKFLOW.md` for your use case

---

## 📋 Checklist for Mobile Success

- [ ] Installed Termux (Android) or iSH (iOS)
- [ ] Cloned the repository
- [ ] Read MOBILE_WORKFLOW.md
- [ ] Decided: Cloud or local?
- [ ] Understood time requirements
- [ ] Checked available storage
- [ ] Ready to start!

---

## Remember

**Mobile is great for:**
✅ Reading docs
✅ Code review  
✅ Git operations
✅ Analysis

**Cloud is better for:**
⚡ Pipeline execution
⚡ Video processing
⚡ Model downloads

**Use the right tool for each task!**

---

**Start here:** `cat MOBILE_WORKFLOW.md | less`

**Good luck! 🚀**
