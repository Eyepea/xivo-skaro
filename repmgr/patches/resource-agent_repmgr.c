diff --git a/repmgr.c b/repmgr.c
index e493b12..8c93f08 100644
--- a/repmgr.c
+++ b/repmgr.c
@@ -45,6 +45,8 @@
 #define STANDBY_CLONE 	 3
 #define STANDBY_PROMOTE  4
 #define STANDBY_FOLLOW 	 5
+#define STATE_CHECK      6
+#define STATE_VALIDATE   7
 
 static void help(const char *progname);
 static bool create_recovery_file(const char *data_dir, char *master_conninfo);
@@ -57,6 +59,7 @@ static void do_standby_register(void);
 static void do_standby_clone(void);
 static void do_standby_promote(void);
 static void do_standby_follow(void);
+static void do_state_check(void);
 static void help(const char* progname);
 static void usage(void);
 
@@ -116,7 +119,6 @@ main(int argc, char **argv)
 		}
 	}
 
-
 	while ((c = getopt_long(argc, argv, "d:h:p:U:D:f:R:w:F:v", long_options,
 	                        &optindex)) != -1)
 	{
@@ -175,7 +177,8 @@ main(int argc, char **argv)
 	{
 		server_mode = argv[optind++];
 		if (strcasecmp(server_mode, "STANDBY") != 0 &&
-		        strcasecmp(server_mode, "MASTER") != 0)
+		    strcasecmp(server_mode, "MASTER") != 0 &&
+	        strcasecmp(server_mode, "STATE") != 0)
 		{
 			usage();
 			exit(ERR_BAD_CONFIG);
@@ -204,13 +207,14 @@ main(int argc, char **argv)
 			action = STANDBY_PROMOTE;
 		else if (strcasecmp(server_cmd, "FOLLOW") == 0)
 			action = STANDBY_FOLLOW;
+		else if (strcasecmp(server_cmd, "CHECK") == 0)
+			action = STATE_CHECK;
 		else
 		{
 			usage();
 			exit(ERR_BAD_CONFIG);
 		}
 	}
-
 	/* For some actions we still can receive a last argument */
 	if (action == STANDBY_CLONE)
 	{
@@ -314,6 +318,9 @@ main(int argc, char **argv)
 	case STANDBY_FOLLOW:
 		do_standby_follow();
 		break;
+	case STATE_CHECK:
+		do_state_check();
+		break;
 	default:
 		usage();
 		exit(ERR_BAD_CONFIG);
@@ -849,6 +856,7 @@ do_standby_clone(void)
 				PQfinish(conn);
 				exit(ERR_BAD_CONFIG);
 			}
+			break;
 		default:
 			/* Trouble accessing directory */
 			log_err(_("%s: could not access directory \"%s\": %s\n"),
@@ -1313,6 +1321,25 @@ do_standby_follow(void)
 }
 
 
+static void
+do_state_check(void)
+{
+	PGconn		*conn;
+
+	log_info(_("%s connecting to standby database\n"), progname);
+	conn = establishDBConnection(options.conninfo, true);
+
+	/* Check we are a standby */
+	if (!is_standby(conn))
+	{
+		PQfinish(conn);
+		exit(IS_MASTER);
+	}
+	PQfinish(conn);
+	return;
+}
+
+
 void usage(void)
 {
 	log_err(_("\n\n%s: Replicator manager \n"), progname);
@@ -1326,6 +1353,7 @@ void help(const char *progname)
 	printf(_(" %s [OPTIONS] master	{register}\n"), progname);
 	printf(_(" %s [OPTIONS] standby {register|clone|promote|follow}\n"),
 	       progname);
+	printf(_(" %s [OPTIONS] state	{check}\n"), progname);
 	printf(_("\nGeneral options:\n"));
 	printf(_("	--help					   show this help, then exit\n"));
 	printf(_("	--version				   output version information, then exit\n"));
@@ -1352,6 +1380,7 @@ void help(const char *progname)
 	printf(_(" standby promote		 - allows manual promotion of a specific standby into a "));
 	printf(_("new master in the event of a failover\n"));
 	printf(_(" standby follow		 - allows the standby to re-point itself to a new master\n"));
+	printf(_(" state check			 - check state of the current node\n\n"));
 }
 
 
@@ -1628,6 +1657,9 @@ check_parameters_for_action(const int action)
 		}
 		need_a_node = false;
 		break;
+	case STATE_CHECK:
+		need_a_node = false;
+		break;
 	}
 
 	return ok;
