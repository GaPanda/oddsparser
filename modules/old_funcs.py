def hasNoClassA(tag): #Возвращает строки не имеющие класса
    return not tag.has_attr	('class') and tag.name == 'a'
