/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.model;

import javafx.scene.control.CheckBox;
import javafx.scene.control.Label;

/**
 *
 * @author lehmann
 */
public class AirtoolsTask {
    private final String funcName;
    private final CheckBox cb;
    private final Label status;

    public AirtoolsTask(String funcName, CheckBox cb, Label status) {
        this.funcName = funcName;
        this.cb = cb;
        this.status = status;
    }

    public String getFuncName() {
        return funcName;
    }

    public String getDescription() {
        return cb.getText();
    }

    public boolean isSelected() {
        return cb.isSelected();
    }
    
    public void deSelect() {
        cb.selectedProperty().set(false);
    }

    public String getStatus() {
        return status.getText();
    }

    public void setStatus(String status) {
        this.status.setText(status);
    }
    
}
