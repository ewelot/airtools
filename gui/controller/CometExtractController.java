/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.controller;

import java.io.File;
import java.io.FilenameFilter;
import java.net.URL;
import java.util.Arrays;
import java.util.ResourceBundle;
import java.util.regex.Pattern;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.CheckBox;
import javafx.scene.control.ComboBox;
import javafx.scene.control.DialogPane;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import tl.airtoolsgui.model.ImageSet;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class CometExtractController implements Initializable {

    @FXML
    private DialogPane paramDialogPane;
    @FXML
    private TextField tfImageSet;
    @FXML
    private TextField tfBgImage;
    @FXML
    private ComboBox<String> cbCoMult;
    @FXML
    private ComboBox<String> cbMaxRadius;
    @FXML
    private Label labelDelete;
    @FXML
    private CheckBox cbDelete;
    @FXML
    private Label labelWarning;

    private ImageSet imgSet;

    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        // disable unimplemented checkbox
        //cbDelete.setDisable(true);
        
        labelWarning.setText("");
        cbCoMult.getItems().addAll("1", "3", "10");
        cbMaxRadius.getItems().addAll("10", "100");
    }    
    
    public void setImageSet(ImageSet imgSet) {
        if (imgSet != null) {
            if (imgSet.equals(this.imgSet)) {
                resetValues();
            } else {
                this.imgSet = imgSet;
                tfImageSet.setText(imgSet.toString());
                setDefaultValues();
            }
        } else {
            tfImageSet.setText("");
        }
    }
    
    private void resetValues() {
        /* reset widgets when the dialog window is shown again (same image set) */        
        tfBgImage.setText(getBgImage());
        cbDelete.setSelected(false);
    }

    private void setDefaultValues() {
        /* initialize widgets with default values upon change of image set */
        tfBgImage.setText(getBgImage());
        cbCoMult.setValue("10");
        cbMaxRadius.setValue("10");
        cbDelete.setSelected(false);
    }

    private String getBgImage() {
        String bgImage="";
        
        // choose the latest bgcorr image
        final String patternStr =
            imgSet.getSetname() + ".bgm[0-9]+.fits"     + "|" +
            imgSet.getSetname() + ".bgm[0-9]+all.fits"  + "|" +
            imgSet.getSetname() + ".bgm[0-9]+.p[pg]m"   + "|" +
            imgSet.getSetname() + ".bgm[0-9]+all.p[pg]m"
            ;
        System.out.println("# pattern = " + patternStr);
        File bgcorrDir = new File(imgSet.getProjectDir() + "/bgcorr");
        if (bgcorrDir.exists()) {
            File[] matchedFiles=bgcorrDir.listFiles(new FilenameFilter() {
                    final private Pattern pattern = Pattern.compile(patternStr);

                    @Override
                    public boolean accept(File dir, String name) {
                        return pattern.matcher(new File(name).getName()).matches();
                    }
                });
            if (matchedFiles.length > 0) {
                //logger.log("# number of matched files = " + matchedFiles.length);
                File mostRecentBgImage = Arrays
                    .stream(matchedFiles)
                    .filter(f -> f.isFile())
                    .max(
                        (f1, f2) -> Long.compare(f1.lastModified(),
                            f2.lastModified())).get();

                if (mostRecentBgImage.exists())
                    bgImage = "bgcorr/" + mostRecentBgImage.getName();
            }
        }
        return bgImage;        
    }
    
    public boolean getOverwrite() {
        return cbDelete.isSelected();
    }

    public String[] getValues() {
        String[] sarray;
        sarray = new String[] {tfBgImage.getText()
                ,cbCoMult.getValue()
                ,cbMaxRadius.getValue()
        };
        return sarray;
    }
}
