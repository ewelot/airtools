/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.model;

import java.text.SimpleDateFormat;
import javafx.application.Platform;
import javafx.scene.control.CheckBox;
import javafx.scene.control.Label;
import javafx.scene.control.TextArea;

/**
 *
 * @author lehmann
 */
public class SimpleLogger {
    
    private TextArea logArea;
    private CheckBox autoScroll;
    private Label statusLine;
    
    public SimpleLogger () {
    }
    
    public SimpleLogger (TextArea logArea, Label statusLine) {
        this.logArea = logArea;
        this.statusLine = statusLine;
    }

    public SimpleLogger (TextArea logArea, CheckBox autoScroll, Label statusLine) {
        this.logArea = logArea;
        this.autoScroll = autoScroll;
        this.statusLine = statusLine;
    }

    public void setStatusLine(Label statusLine) {
        this.statusLine = statusLine;
    }

    public void setLogArea(TextArea logArea) {
        this.logArea = logArea;
    }

    public void setAutoScroll(CheckBox autoScroll) {
        this.autoScroll = autoScroll;
    }

    public void logTime (String msg) {
        if (msg.isEmpty()) return;
        SimpleDateFormat fmt = new SimpleDateFormat ("[yyyy-MM-dd HH:mm:ss.SSS] ");
        if (logArea==null) {
            System.out.println(fmt.format(new java.util.Date()) + msg);
        } else {
            logArea.appendText(fmt.format(new java.util.Date()) + msg + '\n');
            if (autoScroll==null || autoScroll.isSelected()) {
                logArea.selectPositionCaret(logArea.getLength());
                logArea.deselect();
            }
        }
    }
    
    public void log (String msg) {
        //if (msg.isEmpty()) return;
        if (logArea==null) {
            System.out.println(msg);
        } else {
            Platform.runLater(() -> {
                int caretPosition = logArea.caretPositionProperty().get();
                logArea.appendText(msg + '\n');
                if (autoScroll!=null && ! autoScroll.isSelected()) {
                    logArea.positionCaret(caretPosition);
                }
            });
        }
    }
    
    public void log (Exception e) {
        if (e!=null)
        {
            if (logArea==null) {
                System.out.println(e);
            } else {
                Platform.runLater(() -> {
                    this.log(e.toString());
                    StackTraceElement calls[] = e.getStackTrace();
                    int callno=0;
                    while(callno<calls.length)
                    {
                        logArea.appendText("        [Stacktrace] " + calls[callno].toString() + '\n');
                        callno++;
                    }
                    logArea.appendText("\n");
                    if (autoScroll==null || autoScroll.isSelected()) {
                        logArea.selectPositionCaret(logArea.getLength());
                        logArea.deselect();
                    }
                });
            }
        }
    }
    
    public void statusLog (String msg) {
        //log(msg);
        if (statusLine != null)
            Platform.runLater(() -> {
                statusLine.setText(msg);
            });
    }
    
    public void clearStatus () {
        if (statusLine != null)
            Platform.runLater(() -> {
                statusLine.setText("");
            });
    }
}
