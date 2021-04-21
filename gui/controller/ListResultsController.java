/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.controller;

import java.io.File;
import java.net.URL;
import java.time.format.DateTimeFormatter;
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
import javafx.scene.control.ChoiceBox;
import javafx.scene.control.DatePicker;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import javafx.scene.layout.AnchorPane;
import javafx.stage.DirectoryChooser;
import javafx.stage.Stage;
import tl.airtoolsgui.model.AirtoolsCLICommand;
import tl.airtoolsgui.model.ShellScript;
import tl.airtoolsgui.model.SimpleLogger;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class ListResultsController implements Initializable {

    @FXML
    private AnchorPane paneListResults;
    @FXML
    private TextField tfBaseDir1;
    @FXML
    private Button buttonBrowseBaseDir1;
    @FXML
    private TextField tfBaseDir2;
    @FXML
    private Button buttonBrowseBaseDir2;
    @FXML
    private TextField tfCometName;
    @FXML
    private DatePicker dpStart;
    @FXML
    private DatePicker dpEnd;
    @FXML
    private ChoiceBox<String> cbInstrument;
    @FXML
    private CheckBox cbShowUncalibrated;
    @FXML
    private Label labelWarning;
    @FXML
    private Button buttonStart;
    @FXML
    private Button buttonCancel;

    private SimpleLogger logger;
    private StringProperty projectDir = new SimpleStringProperty();
    private AirtoolsCLICommand aircliCmd;
    private final String aircliTask = "usercmd";
    private final String airfunFunc = "AIlist";

    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        // fill combo boxes
        // TODO: get valid instruments from camera.dat
        cbInstrument.getItems().setAll("any");
        cbInstrument.getSelectionModel().selectFirst();
    }    

    public void setReferences (ShellScript sh, SimpleLogger logger, StringProperty projectDir) {
        this.logger = logger;
        this.projectDir = projectDir;
        this.aircliCmd = new AirtoolsCLICommand(buttonStart, logger, sh);

        setBaseDirectories();
        labelWarning.setText("");
    }
    
    private void setBaseDirectories () {
        String base;
        File f;

        /* set project base directory */
        f = new File(projectDir.getValue());
        base=f.getParent();
        tfBaseDir1.setText(base);

        /* set secondary base directory (results dir) */
        /*
        f = new File(base + "/results");
        if (f.exists() && f.isDirectory()) {
            tfBaseDir2.setText(f.getAbsolutePath());
        }
        */
    }
    
    @FXML
    private void onButtonBrowseBaseDir1(ActionEvent event) {
        DirectoryChooser dirChooser = new DirectoryChooser();
        String dirName = tfBaseDir1.getText();
        File f;
        
        if (dirName.isEmpty()) {
            f = new File(projectDir.getValue());
            dirName=f.getParent();
        }

        File file = new File(dirName);
        if (! file.isDirectory()) {
            dirName = file.getParent();
            file = new File(dirName);
            if (! file.isDirectory()) {
                dirName = file.getParent();
                file = new File(dirName);
                if (! file.isDirectory()) {
                    f = new File(projectDir.getValue());
                    dirName=f.getParent();
                    file = new File(dirName);
                }
            }
        }
        dirChooser.setInitialDirectory(file);
        Stage stage = (Stage) paneListResults.getScene().getWindow();
        file = dirChooser.showDialog(stage);
        if (file != null) {
            // TODO: check if dir exists and is empty, else show a warning message
            tfBaseDir1.setText(file.getAbsolutePath());
        }
    }

    @FXML
    private void onButtonBrowseBaseDir2(ActionEvent event) {
        DirectoryChooser dirChooser = new DirectoryChooser();
        String dirName = tfBaseDir2.getText();
        File f;
        
        if (dirName.isEmpty()) {
            f = new File(projectDir.getValue());
            dirName=f.getParent();
        }

        File file = new File(dirName);
        if (! file.isDirectory()) {
            dirName = file.getParent();
            file = new File(dirName);
            if (! file.isDirectory()) {
                dirName = file.getParent();
                file = new File(dirName);
                if (! file.isDirectory()) {
                    f = new File(projectDir.getValue());
                    dirName=f.getParent();
                    file = new File(dirName);
                }
            }
        }
        dirChooser.setInitialDirectory(file);
        Stage stage = (Stage) paneListResults.getScene().getWindow();
        file = dirChooser.showDialog(stage);
        if (file != null) {
            // TODO: check if dir exists and is empty, else show a warning message
            tfBaseDir2.setText(file.getAbsolutePath());
        }
    }

    @FXML
    private void onButtonStart(ActionEvent event) {
        System.out.println("ListResultsController: onButtonStart()");
        labelWarning.setText("");
        List<String> aircliCmdOpts = new ArrayList<>();
        List<String> aircliCmdArgs = new ArrayList<>();

        DateTimeFormatter fmt = DateTimeFormatter.ofPattern("YYMMdd");
        String instrument=cbInstrument.getSelectionModel().getSelectedItem();
        
        //if (! isValidInputs()) return;
        // airfun function to call
        aircliCmdArgs.add(airfunFunc);
                
        // add options
        if (cbShowUncalibrated.isSelected()) aircliCmdArgs.add("-a");
        if (! instrument.equalsIgnoreCase("any")) aircliCmdArgs.add("-t " + instrument);
        
        if (! tfBaseDir1.getText().isBlank()) aircliCmdArgs.add("-d " + tfBaseDir1.getText());
        if (! tfBaseDir2.getText().isBlank()) aircliCmdArgs.add("-d " + tfBaseDir2.getText());
        
        // add parameters
        if (! tfCometName.getText().isBlank()) {
            aircliCmdArgs.add(tfCometName.getText());
        } else {
            if (dpStart.getValue() != null || dpEnd.getValue() != null)
                aircliCmdArgs.add("\"\"");
        }
        if (dpStart.getValue() != null) {
            aircliCmdArgs.add(dpStart.getValue().format(fmt));
        } else {
            if (dpEnd.getValue() != null)
                aircliCmdArgs.add("\"\"");
        }
        if (dpEnd.getValue() != null) {
            aircliCmdArgs.add(dpEnd.getValue().format(fmt));
        }
        
        // run command
        System.out.println("cmd: " + aircliCmdOpts + " " + aircliTask + " " + aircliCmdArgs);
        logger.log("# cmd: " + aircliCmdOpts + " " + aircliTask + " " + aircliCmdArgs);
        aircliCmd.setOpts(aircliCmdOpts.toArray(new String[0]));
        aircliCmd.setArgs(aircliCmdArgs.toArray(new String[0]));
        aircliCmd.run();
    }

    @FXML
    private void onButtonCancel(ActionEvent event) {
        Node  source = (Node)  event.getSource(); 
        Stage stage  = (Stage) source.getScene().getWindow();
        stage.close();
    }
    
}
