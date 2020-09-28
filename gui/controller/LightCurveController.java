/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.controller;

import java.io.File;
import java.net.URL;
import java.time.format.DateTimeFormatter;
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
import javafx.stage.FileChooser;
import javafx.stage.Stage;
import tl.airtoolsgui.model.AirtoolsCLICommand;
import tl.airtoolsgui.model.ShellScript;
import tl.airtoolsgui.model.SimpleLogger;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class LightCurveController implements Initializable {

    @FXML
    private AnchorPane paneLightCurve;
    @FXML
    private TextField tfCometName;
    @FXML
    private TextField tfICQFile;
    @FXML
    private Button buttonBrowseICQFile;
    @FXML
    private CheckBox cbUseCOBS;
    @FXML
    private CheckBox cbScanLocalProjects;
    @FXML
    private CheckBox cbForceUpdate;
    @FXML
    private ChoiceBox<PlotType> cbPlotType;
    @FXML
    private DatePicker dpStart;
    @FXML
    private DatePicker dpEnd;
    @FXML
    private TextField tfObsList;
    @FXML
    private ChoiceBox<KeyPosition> cbKeyPosition;
    @FXML
    private TextField tfAddOptions;
    @FXML
    private ChoiceBox<FitType> cbFitType;
    @FXML
    private TextField tfModelM;
    @FXML
    private TextField tfModelN;
    @FXML
    private CheckBox cbMPCModel;
    @FXML
    private CheckBox cbDistance;
    @FXML
    private Label labelWarning;
    
    @FXML
    private Button buttonStart;
    @FXML
    private Button buttonCancel;

    private SimpleLogger logger;
    private StringProperty projectDir = new SimpleStringProperty();
    private AirtoolsCLICommand airCmd;

    
    private enum PlotType {
        MAG("Observed Magnitude"),
        HMAG("Heliocentric Magnitude"),
        COMA("Apparent Coma Diameter"),
        LCOMA("Linear Coma Diameter");

        private final String label;

        PlotType(String label) {
            this.label = label;
        }

        @Override
        public String toString() {
            return label;
        }
    }

    private enum FitType {
        NONE("none", ""),
        ALL("all available data", "-f"),
        LIST("data matching observers list", "-ff");
        
        private final String label;
        private final String option;

        FitType(String label, String option) {
            this.label = label;
            this.option = option;
        }

        public String getOption() {
            return option;
        }
        
        @Override
        public String toString() {
            return label;
        }
    }
    
    private enum KeyPosition {
        TOPLEFT("top left",         "-k top_left_reverse_Left_invert"),
        TOPRIGHT("top right",       "-k top_right_reverse_Left_invert"),
        BOTTOMLEFT("bottom left",   "-k bottom_left_reverse_Left_invert"),
        BOTTOMRIGHT("bottom right", "-k bottom_right_reverse_Left_invert");
        
        private final String label;
        private final String option;
        
        KeyPosition(String label, String option) {
            this.label = label;
            this.option = option;
        }
        
        public String getOption() {
            return option;
        }
        
        @Override
        public String toString() {
            return label;
        }
    }
    
    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        // fill combo boxes
        cbPlotType.getItems().setAll(PlotType.values());
        cbPlotType.getSelectionModel().select(PlotType.MAG);

        cbFitType.getItems().setAll(FitType.values());
        cbFitType.getSelectionModel().select(FitType.ALL);
        
        cbKeyPosition.getItems().setAll(KeyPosition.values());
        cbKeyPosition.getSelectionModel().select(KeyPosition.TOPLEFT);
        
        paneLightCurve.setOnMouseClicked(event -> {
            labelWarning.setText("");
        });
    }
    
    
    public void setReferences (ShellScript sh, SimpleLogger logger, StringProperty projectDir) {
        this.logger = logger;
        this.projectDir = projectDir;
        this.airCmd = new AirtoolsCLICommand(buttonStart, logger, sh);

        labelWarning.setText("");
    }
    

    private boolean isValidInputs() {
        String msg="";
        if (tfCometName.getText().isBlank()) {
            msg="ERROR: comet name is missing.";
            labelWarning.setText(msg);
            logger.log(msg);
            return false;
        }
        return true;
    }
    
    
    @FXML
    private void onButtonBrowseICQFile(ActionEvent event) {
        FileChooser fileChooser = new FileChooser();
        String dirName = "";
        
        if (! tfICQFile.getText().isBlank()) {
            File f = new File(tfICQFile.getText());
            dirName = f.getParent();
        }
        if (dirName.isBlank()) dirName = projectDir.getValue();
        if (dirName.isBlank()) dirName = System.getProperty("user.home");

        fileChooser.setInitialDirectory(new File(dirName));
        File file = fileChooser.showOpenDialog(this.paneLightCurve.getScene().getWindow());
        if (file.exists()) {
            tfICQFile.setText(file.getAbsolutePath());
        }
    }

    
    @FXML
    private void onDpStart(ActionEvent event) {
    }

    @FXML
    private void onDpEnd(ActionEvent event) {
    }

    @FXML
    private void onButtonStart(ActionEvent event) {
        System.out.println("LightCurveController: onButtonStart()");
        labelWarning.setText("");
        if (! isValidInputs()) return;
        String cmd="icqplot";
        PlotType plotType=cbPlotType.getSelectionModel().getSelectedItem();
        FitType fitType=cbFitType.getSelectionModel().getSelectedItem();
        KeyPosition keyPos=cbKeyPosition.getSelectionModel().getSelectedItem();

        // add options
        if (cbUseCOBS.isSelected())           cmd+=" -c";
        if (cbScanLocalProjects.isSelected()) cmd+=" -l";
        if (cbForceUpdate.isSelected())       cmd+=" -u";
        if (cbMPCModel.isSelected())          cmd+=" -m";
        if (cbDistance.isSelected())          cmd+=" -d";
        if (fitType != FitType.NONE)          cmd+=" " + fitType.getOption();
        if (keyPos  != KeyPosition.TOPLEFT)   cmd+=" " + keyPos.getOption();
        
        if (dpStart.getValue() != null || dpEnd.getValue() != null) {
            cmd+=" -x";
            cmd+=" ";
            DateTimeFormatter fmt = DateTimeFormatter.ofPattern("YYYYMMdd");
            if (dpStart.getValue() != null) {
                cmd+=dpStart.getValue().format(fmt);
            }
            if (dpEnd.getValue() != null) {
                cmd+=":" + dpEnd.getValue().format(fmt);
            }
        }
        
        if (! tfModelM.getText().isBlank() && ! tfModelN.getText().isBlank()) {
            cmd+=" -n " + tfModelM.getText() + "," + tfModelN.getText();
        }
        
        if (! tfObsList.getText().isBlank()) {
            cmd+=" -i \"" + tfObsList.getText() + "\"";
        }
        
        if (! tfAddOptions.getText().isBlank()) {
            cmd+=" " + tfAddOptions.getText();
        }
        
        // add positional parameters
        cmd+=" " + tfCometName.getText();
        if (! tfICQFile.getText().isBlank()) {
            cmd+=" " + tfICQFile.getText();
        } else {
            cmd+=" \"\"";
        }
        cmd+=" " + plotType.name().toLowerCase();
        
        // run command
        System.out.println("cmd: " + cmd);
        logger.log("# cmd: " + cmd);
        airCmd.setArgs(cmd.split("\\s+"));
        airCmd.run();
    }
    
    @FXML
    private void onButtonCancel(ActionEvent event) {
        Node  source = (Node)  event.getSource(); 
        Stage stage  = (Stage) source.getScene().getWindow();
        stage.close();
    }
}
