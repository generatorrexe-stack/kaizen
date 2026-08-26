import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15
import QtQml.Models 2.15
import "./components"

Rectangle {
    id: root
    height: Screen.height
    width: Screen.width
    color: "{{bg}}"

    property string musicText: "Loading..."
    property string locationText: "..."
    property int batteryPct: 0
    property double inputHeight: Screen.height * 0.175 * 0.25 * config.Scale
    property double inputWidth: Screen.width * 0.175 * config.Scale

    DelegateModel {
        id: userWrapper
        model: userModel
        delegate: Item {}
    }

    Image {
        id: bg
        anchors.fill: parent
        source: config.BgSource
        fillMode: Image.PreserveAspectCrop
        clip: true
    }

    Rectangle { anchors.fill: parent; color: "{{bg}}"; opacity: 0.55 }

    Text {
        anchors { top: parent.top; horizontalCenter: parent.horizontalCenter; topMargin: 110 }
        text: Qt.formatTime(new Date(), "h:mm AP")
        color: "{{accent}}"
        font.pixelSize: 90
        font.bold: true
        font.family: config.FontFamily

        Timer {
            interval: 1000
            running: true
            repeat: true
            onTriggered: parent.text = Qt.formatTime(new Date(), "h:mm AP")
        }
    }

    Text {
        anchors { top: parent.top; horizontalCenter: parent.horizontalCenter; topMargin: 213 }
        text: Qt.formatDate(new Date(), "dddd, d MMMM")
        color: "{{accent2}}"
        font.pixelSize: 26
        font.bold: true
        font.family: config.FontFamily
    }

    Column {
        anchors.centerIn: parent
        anchors.verticalCenterOffset: 60
        spacing: 24

        Rectangle {
            id: avatarBorder
            anchors.horizontalCenter: parent.horizontalCenter
            width: 180
            height: 180
            radius: 90
            color: "{{bg}}"
            border.width: 5
            border.color: "{{accent}}"

            SequentialAnimation on border.color {
                loops: Animation.Infinite
                ColorAnimation { to: "{{accent2}}"; duration: 1800 }
                ColorAnimation { to: "{{accent}}"; duration: 1800 }
            }

            Image {
                id: userPicture
                anchors.centerIn: parent
                width: 170
                height: 170
                source: "file:/home/wonyoung/Documents/banners/foto123-circle.png"
                fillMode: Image.PreserveAspectFit
                antialiasing: true
                smooth: true
            }
        }

        Text {
            id: usernameText
            anchors.horizontalCenter: parent.horizontalCenter
            text: "user"
            color: "{{fg}}"
            font.pixelSize: 30
            font.bold: true
            font.family: config.FontFamily
        }

        TextField {
            id: passwordField
            anchors.horizontalCenter: parent.horizontalCenter
            width: 320
            height: 54
            echoMode: TextInput.Password
            placeholderText: "password"
            color: "{{fg}}"
            font.pixelSize: 16
            font.family: config.FontFamily
            horizontalAlignment: TextInput.AlignHCenter

            background: Rectangle {
                radius: 27
                color: "{{bg}}"
                opacity: 0.7
                border.width: 2
                border.color: "{{accent2}}"
            }

            onAccepted: loginBtn.clicked()
        }

        Button {
            id: loginBtn
            anchors.horizontalCenter: parent.horizontalCenter
            width: 320
            height: 54

            contentItem: Text {
                text: "LOGIN"
                color: "{{bg}}"
                font.bold: true
                font.pixelSize: 16
                font.family: config.FontFamily
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }

            background: Rectangle {
                radius: 27
                color: "{{accent}}"
            }

            onClicked: {
                sddm.login(usernameText.text, passwordField.text, sessionButton.currentIndex)
            }
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "THE WINNER TAKES IT ALL"
            color: "{{purple}}"
            font.pixelSize: 13
            font.letterSpacing: 2
            font.family: config.FontFamily
            opacity: 0.8
        }
    }

    Column {
        anchors { bottom: parent.bottom; left: parent.left; margins: 45 }
        spacing: 12

        Row {
            spacing: 10
            Text { text: "🔋"; font.pixelSize: 22 }
            Text { text: batteryPct + "%"; color: "{{accent2}}"; font.pixelSize: 19; font.bold: true; font.family: config.FontFamily }
        }
        Row {
            spacing: 10
            Text { text: "📍"; font.pixelSize: 22 }
            Text { text: locationText; color: "{{fg}}"; font.pixelSize: 19; font.family: config.FontFamily }
        }
    }

    Row {
        anchors { bottom: parent.bottom; right: parent.right; margins: 45 }
        spacing: 12

        Row {
            spacing: 3
            anchors.verticalCenter: parent.verticalCenter
            Repeater {
                model: 4
                Rectangle {
                    width: 4
                    radius: 2
                    color: "{{accent}}"
                    height: 8
                    anchors.bottom: parent.bottom

                    SequentialAnimation on height {
                        loops: Animation.Infinite
                        NumberAnimation { to: 6 + Math.random() * 16; duration: 300 + index * 80; easing.type: Easing.InOutSine }
                        NumberAnimation { to: 6 + Math.random() * 16; duration: 300 + index * 80; easing.type: Easing.InOutSine }
                    }
                }
            }
        }

        Text { text: musicText; color: "{{accent}}" ; font.pixelSize: 19; font.family: config.FontFamily; anchors.verticalCenter: parent.verticalCenter }
    }

    SessionPanel { id: sessionButton; visible: false }

    Rectangle {
        id: topMenuBtn
        anchors { top: parent.top; right: parent.right; margins: 30 }
        width: 46
        height: 46
        radius: 23
        color: "{{bg}}"
        opacity: 0.75
        border.width: 2
        border.color: "{{accent}}"
        z: 10

        Text {
            anchors.centerIn: parent
            text: "󰣇"
            color: "{{accent}}"
            font.pixelSize: 22
            font.family: config.FontFamily
        }

        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            onClicked: topMenuPopup.visible = !topMenuPopup.visible
        }
    }

    Rectangle {
        id: topMenuPopup
        anchors { top: topMenuBtn.bottom; right: parent.right; margins: 30; topMargin: 10 }
        width: 220
        height: menuCol.implicitHeight + 20
        radius: 16
        color: "{{bg_alt}}"
        opacity: 0.95
        border.width: 2
        border.color: "{{accent2}}"
        visible: false
        z: 10

        Column {
            id: menuCol
            anchors { fill: parent; margins: 10 }
            spacing: 4

            Repeater {
                model: sessionButton.model
                delegate: Rectangle {
                    width: parent.width
                    height: 36
                    radius: 10
                    color: sessionMouseArea.containsMouse ? "{{accent}}" : "transparent"

                    Row {
                        anchors { left: parent.left; verticalCenter: parent.verticalCenter; leftMargin: 12 }
                        spacing: 8
                        Text { text: "🐧"; font.pixelSize: 14 }
                        Text {
                            text: name
                            color: sessionMouseArea.containsMouse ? "{{bg}}" : "{{fg}}"
                            font.pixelSize: 14
                            font.family: config.FontFamily
                        }
                    }

                    MouseArea {
                        id: sessionMouseArea
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: {
                            sessionButton.currentIndex = index
                            topMenuPopup.visible = false
                        }
                    }
                }
            }

            Rectangle { width: parent.width; height: 1; color: "{{accent}}"; opacity: 0.3 }

            Rectangle {
                width: parent.width
                height: 36
                radius: 10
                color: suspendArea.containsMouse ? "{{accent2}}" : "transparent"

                Row {
                    anchors { left: parent.left; verticalCenter: parent.verticalCenter; leftMargin: 12 }
                    spacing: 8
                    Text { text: "🌙"; font.pixelSize: 14 }
                    Text { text: "Suspend"; color: suspendArea.containsMouse ? "{{bg}}" : "{{fg}}"; font.pixelSize: 14; font.family: config.FontFamily }
                }

                MouseArea {
                    id: suspendArea
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: sddm.suspend()
                }
            }

            Rectangle {
                width: parent.width
                height: 36
                radius: 10
                color: hibernateArea.containsMouse ? "{{purple}}" : "transparent"

                Row {
                    anchors { left: parent.left; verticalCenter: parent.verticalCenter; leftMargin: 12 }
                    spacing: 8
                    Text { text: "❄️"; font.pixelSize: 14 }
                    Text { text: "Hibernate"; color: hibernateArea.containsMouse ? "{{bg}}" : "{{fg}}"; font.pixelSize: 14; font.family: config.FontFamily }
                }

                MouseArea {
                    id: hibernateArea
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: sddm.hibernate()
                }
            }

            Rectangle { width: parent.width; height: 1; color: "{{accent2}}"; opacity: 0.3 }

            Rectangle {
                width: parent.width
                height: 36
                radius: 10
                color: shutdownArea.containsMouse ? "{{accent}}" : "transparent"

                Row {
                    anchors { left: parent.left; verticalCenter: parent.verticalCenter; leftMargin: 12 }
                    spacing: 8
                    Text { text: "⏻"; color: shutdownArea.containsMouse ? "{{bg}}" : "{{accent}}"; font.pixelSize: 15 }
                    Text { text: "Shut Down"; color: shutdownArea.containsMouse ? "{{bg}}" : "{{fg}}"; font.pixelSize: 14; font.family: config.FontFamily }
                }

                MouseArea {
                    id: shutdownArea
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: sddm.powerOff()
                }
            }

            Rectangle {
                width: parent.width
                height: 36
                radius: 10
                color: rebootArea.containsMouse ? "{{accent2}}" : "transparent"

                Row {
                    anchors { left: parent.left; verticalCenter: parent.verticalCenter; leftMargin: 12 }
                    spacing: 8
                    Text { text: "⟳"; color: rebootArea.containsMouse ? "{{bg}}" : "{{accent2}}"; font.pixelSize: 15 }
                    Text { text: "Restart"; color: rebootArea.containsMouse ? "{{bg}}" : "{{fg}}"; font.pixelSize: 14; font.family: config.FontFamily }
                }

                MouseArea {
                    id: rebootArea
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: sddm.reboot()
                }
            }
        }
    }

    Connections {
        target: sddm
        function onLoginFailed() {
            passwordField.text = ""
            passwordField.focus = true
        }
    }

    Component.onCompleted: {
        if (userWrapper.count > 0) {
            var idx = userModel.lastIndex >= 0 ? userModel.lastIndex : 0
            var entry = userWrapper.items.get(idx).model
            usernameText.text = entry.name
        }
    }

    Timer {
        interval: 3000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: {
            try {
                var xhrM = new XMLHttpRequest()
                xhrM.open("GET", "file:/tmp/sddm-music.txt", false)
                xhrM.send()
                if (xhrM.readyState === XMLHttpRequest.DONE)
                    musicText = xhrM.responseText.trim()
            } catch (e) {
                musicText = "Not playing"
            }

            try {
                var xhrL = new XMLHttpRequest()
                xhrL.open("GET", "file:/tmp/sddm-location.txt", false)
                xhrL.send()
                if (xhrL.readyState === XMLHttpRequest.DONE)
                    locationText = xhrL.responseText.trim()
            } catch (e) {
                locationText = "Unknown"
            }

            try {
                var xhrB = new XMLHttpRequest()
                xhrB.open("GET", "file:/sys/class/power_supply/BAT0/capacity", false)
                xhrB.send()
                if (xhrB.readyState === XMLHttpRequest.DONE && xhrB.responseText.trim() !== "")
                    batteryPct = parseInt(xhrB.responseText.trim())
            } catch (e) {
                batteryPct = 0
            }
        }
    }
}
