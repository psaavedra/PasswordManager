import passManager
import csv

def get_model_fields(model):
    return model._meta.fields

def get_model_field_names(model):
    res = []
    for field in get_model_fields(model):
        f = field.name
        res.append(f)
    return res

def get_model_fields_values(modelobj):
    res = []
    for field in get_model_fields(modelobj):
        f = str(getattr(modelobj, field.name))
        res.append(f)
    return res

def clone_model(modelobj):
    new = modelobj.__class__()
    for field in get_model_fields(modelobj):
        value = getattr(modelobj, field.name)
        setattr(new,field.name,value)
    return new

def from_model_to_csv_header(model):
    row = ''
    for field in get_model_fields(model):
        f = field.name
        f = f.replace('"','""')
        row += '"' + f + '",'
    return row

def from_model_to_csv_row(modelobj):
    row = ""
    for field in get_model_fields(modelobj):
        f = str(getattr(modelobj, field.name))
        f = f.replace('"','""')
        row += '"' + f + '",'
    return row

def from_model_to_csv(model,q,fileobj):

    writer = csv.writer(fileobj)
    for o in model.objects.filter(q):
        csv_row = from_model_to_csv_row(o)
        writer.writerow(csv_row)


def from_csv_to_model(model,fileobj,extrafunc=None):
    '''
            modelobj = extrafunc(model,modelobj,row,headers)
    '''
    csv_reader = csv.reader(fileobj)
    headers = csv_reader.next()
    for row in csv_reader:
        modelobj = None
        try:
            index_id = headers.index("id")
            modelobj = model.objects.get(id=row[index_id])
        except Exception, e:
            pass
        if extrafunc:
            modelobj = extrafunc(model,modelobj,row, headers)

        if not modelobj:
            modelobj = model()

        for i in range(0,len(row)-1):
            try:
                header = headers[i]
                value = row[i]
                if header == "id":
                    continue
                if value in ["True", "False"]:
                    value = eval(value)
                try:
                    from dateutil.parser import parse
                    value = parse(value)
                except Exception, e:
                    pass

                # print "header: %s value: %s" % (header, value)
                old_value = getattr(modelobj,header)
                setattr(modelobj,header, value)
                try:
                    modelobj.save()
                except Exception, e:
                    setattr(modelobj,header, old_value)
            except Exception, e:
                pass

