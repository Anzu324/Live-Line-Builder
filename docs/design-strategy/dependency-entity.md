# Entity一覧
- Preset
	- EquipmentEntity(あくまでも機器の設定であって個別を表さない)
	- EquipmentPortEntity(EquipmentEntityに複数持つことができる)
- Project
	- ProjectDataEntity
	- PerformanceDataEntity(コチラは日程ごとに保持する)
- LineGraph
	- Equipment(ライブで使われる個々の機器)
	- EquipmentPort



```mermaid
---
title: 回線関係のリレーション
---
erDiagram
    EquipmentDefinition ||--o{ EquipmentPortDefinition : "ポート"
    EquipmentDefinition {
        id equip_id
        str name
        str node_type
        int quantity
    }
    EquipmentPortDefinition {
        id port_id
        str name
        float pricePerUnit
    }
    EquipmentInstance ||--o{ PortInstance : "Portを参照"
    EquipmentInstance {
        id equip_node_id
        id performance
    }
    PortInstance {
	    id port_node_id
	    id equip_node_id
	    PortDirection direction
	    id equipment_id
    }
    EquipmentDefinition ||--o{ EquipmentInstance : "参考にする"

```



# クラス実装
```mermaid
classDiagram
class TableEntity{
    +list[Colomn] columns
    -list[list[Any]] rows
    +data(row,column) Any
    +setData(row,column,context) bool
}

TableEntity <|-- EquipmentDefinition
TableEntity <|-- EquipmentPortDefinition

DataManger o-- EquipmentDefinition
DataManger o-- EquipmentPortDefinition
DataManger o-- PerformanceGroup
PerformanceGroup *--AudioPatchSystem

AudioPatchSystem *-- EquipmentInstance
AudioPatchSystem *-- PortInstance
EquipmentDefinition <-- EquipmentInstance
EquipmentInstance <--PortInstance
EquipmentPortDefinition <--PortInstance
```



