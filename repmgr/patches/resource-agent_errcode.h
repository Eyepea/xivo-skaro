diff --git a/errcode.h b/errcode.h
index 49433da..fac08cb 100644
--- a/errcode.h
+++ b/errcode.h
@@ -23,6 +23,7 @@
 /* Exit return code */
 
 #define SUCCESS 0
+#define IS_MASTER 100
 #define ERR_BAD_CONFIG 1
 #define ERR_BAD_RSYNC 2
 #define ERR_STOP_BACKUP 3
@@ -33,5 +34,6 @@
 #define ERR_PROMOTED 8
 #define ERR_BAD_PASSWORD 9
 #define ERR_STR_OVERFLOW 10
+#define ERR_INSTALLED 11
 
 #endif	/* _ERRCODE_H_ */
