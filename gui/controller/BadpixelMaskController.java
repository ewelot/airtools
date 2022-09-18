/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.controller;

import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.ResourceBundle;
import javafx.beans.property.SimpleStringProperty;
import javafx.beans.property.StringProperty;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.Node;
import javafx.scene.control.Button;
import javafx.scene.control.CheckBox;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import javafx.scene.layout.AnchorPane;
import javafx.stage.Stage;
import tl.airtoolsgui.model.AirtoolsCLICommand;
import tl.airtoolsgui.model.ShellScript;
import tl.airtoolsgui.model.SimpleLogger;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class BadpixelMaskController implements Initializable {

    @FXML
    private AnchorPane paneBadpixelMask;
    @FXML
    private TextField tfImageSets;
    @FXML
    private TextField tfHot;
    @FXML
    private TextField tfCold;
    @FXML
    private CheckBox cbUseAllSets;
    @FXML
    private CheckBox cbDelete;
    @FXML
    private Label labelWarning;
    @FXML
    private Button buttonStart;
    @FXML
    private Button buttonCancel;

    private SimpleLogger logger;
    private StringProperty projectDir = new SimpleStringProperty();
    private AirtoolsCLICommand aircliCmd;
    private final String aircliTask = "badpix";
    private final String airfunFunc = "";
    
    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        System.out.println("CreateBadpixelMaskController: initialize()");
    }    

    public void setReferences (ShellScript sh, SimpleLogger logger, StringProperty projectDir) {
        System.out.println("CreateBadpixelMaskController: setReferences()");
        this.logger = logger;
        this.projectDir = projectDir;
        this.aircliCmd = new AirtoolsCLICommand(aircliTask, buttonStart, logger, sh);

        labelWarning.setText("");
    }
    
    @FXML
    private void onButtonStart(ActionEvent event) {
        System.out.println("CreateBadpixelMaskController: onButtonStart()");
        labelWarning.setText("");
        List<String> cmdOpts = new ArrayList<>();
        List<String> cmdArgs = new ArrayList<>();
        
        //if (! isValidInputs()) return;
        
        // add options for airtools-cli
        if (cbDelete.isSelected()) cmdOpts.add("-o");
        if (! tfImageSets.getText().isBlank()) {
            //cmdArgs+=" " + tfImageSets.getText();
            cmdOpts.add("-s \"" + tfImageSets.getText() + "\"");
        }
        
        // add task parameters
        if (cbUseAllSets.isSelected()) cmdArgs.add("-a");
        if (tfHot.getText().isBlank()) {
            cmdArgs.add("\"\"");
        } else {
            cmdArgs.add(tfHot.getText());
        }
        if (tfCold.getText().isBlank()) {
            cmdArgs.add("\"\"");
        } else {
            cmdArgs.add(tfCold.getText());
        }
        
        // run airtools-cli command
        System.out.println("cmd: " + cmdOpts + " " + aircliTask + " " + cmdArgs);
        //logger.log("# cmd: " + cmdOpts + " " + aircliTask + " " + cmdArgs);
        aircliCmd.setOpts(cmdOpts.toArray(new String[0]));
        aircliCmd.setArgs(cmdArgs.toArray(new String[0]));
        aircliCmd.run();
    }

    @FXML
    private void onButtonCancel(ActionEvent event) {
        Node  source = (Node)  event.getSource(); 
        Stage stage  = (Stage) source.getScene().getWindow();
        stage.close();
    }
    
}
