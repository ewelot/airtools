/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.model;

import javafx.concurrent.Task;
import javafx.scene.control.Button;

/**
 *
 * @author lehmann
 */
public class AirtoolsCLICommand {
    
    private String cmdName;
    private String[] opts;
    private String[] args;
    private final Button btnStart;

    private final SimpleLogger logger;
    private final ShellScript sh;
    private Task task;

    public AirtoolsCLICommand(String cmdName, Button btn, SimpleLogger logger, ShellScript sh) {
        this.cmdName = cmdName;
        this.logger = logger;
        this.sh = sh;
        this.btnStart = btn;
    }

    public AirtoolsCLICommand(Button btn, SimpleLogger logger, ShellScript sh) {
        this("usercmd", btn, logger, sh);
    }

    public void setCmdName(String cmdName) {
        this.cmdName = cmdName;
    }

    public void setOpts(String[] opts) {
        this.opts = opts;
    }

    public void setArgs(String[] args) {
        this.args = args;
    }

    public void run() {
        String labelStart;
        String colorStart = "#333333";
        String colorStop = "#f00000";
        String str;
        int i;
        
        if (task == null) {
            // ready for new task
            logger.log("");
            //logger.log("# " + "Running ds9cmd " + taskName + opts + args);
            logger.statusLog("Running " + cmdName + " ...");
            labelStart = btnStart.getText();
            btnStart.setText("Stop");
            btnStart.setStyle("-fx-text-fill: " + colorStop);
            
            // convert opts array to optsStr
            str="";
            for (i=0; i<opts.length; i++) {
                 if (! str.isEmpty()) str = str + " ";
                 str = str + opts[i];
            }
            final String optsStr = str;
            //logger.log("argsStr=" + argsStr);
            
            // convert args array to argsStr
            str="";
            for (i=0; i<args.length; i++) {
                 if (! str.isEmpty()) str = str + " ";
                 str = str + args[i];
            }
            final String argsStr = str;
            //logger.log("argsStr=" + argsStr);
            
            task = new Task<Void>() {
                int exitCode=0;

                @Override
                protected Void call() {
                    sh.setEnvVars("");
                    sh.setOpts(optsStr);
                    sh.setArgs(argsStr);
                    //sh.runFunction("\"" + userCmd + "\"");
                    sh.runFunction(cmdName);
                    exitCode=sh.getExitCode();
                    //logger.log("shell script finished with " + exitCode);
                    return null;
                }
            };
            task.setOnSucceeded(e -> {
                if (sh.getExitCode() == 0) {
                    logger.statusLog("Task finished");
                } else {
                    logger.statusLog("Task failed");
                }
                task=null;
                btnStart.setText(labelStart);
                btnStart.setStyle("-fx-text-fill: " + colorStart);
            });
            task.setOnCancelled(e -> {
                logger.statusLog("Task cancelled");
                task=null;
                btnStart.setText(labelStart);
                btnStart.setStyle("-fx-text-fill: " + colorStart);
            });
            Thread thread = new Thread(task);
            thread.setDaemon(true);
            thread.start();
        } else {
            // task is running, interrupt it
            try {
                int exitCode = sh.killProcess();
                if (exitCode != 0) {
                    logger.log("Failed to kill process");
                    logger.statusLog("Failed to kill process");
                } else {
                    task.cancel();
                }
            } catch (Exception ex) {
                logger.log(ex);
                logger.log("Failed to cancel task");
                logger.statusLog("Failed to cancel task");
            }
        }
    }

}
