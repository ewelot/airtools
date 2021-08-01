/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.model;

/**
 *
 * @author lehmann
 */
public class Observer {
    private String name;
    private String address;
    private String email;
    private String icqID;

    public Observer(String name, String address, String email, String icqID) {
        this.name = name;
        this.address = address;
        this.email = email;
        this.icqID = icqID;
    }

    public String getName() {
        return name;
    }

    public String getAddress() {
        return address;
    }

    public String getEmail() {
        return email;
    }

    public String getIcqID() {
        return icqID;
    }

    public void setName(String name) {
        this.name = name;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public void setIcqID(String icqID) {
        this.icqID = icqID;
    }
    
}
